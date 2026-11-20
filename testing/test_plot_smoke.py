import asyncio

import matplotlib.pyplot as plt
from numpy.testing import assert_allclose

from dmtools_libraries.render_core import render_plot_core


def test_render_plot_contains_expected_curve():
    masses = [1, 10, 100]
    cross_sections = [3e-44, 5e-44, 4e-44]
    displays = [
        {
            "properties": {"style": "line", "color": "black"},
            "data": [
                {
                    "properties": {
                        "xUnits": "GeV/c^2",
                        "values": [list(zip(masses, cross_sections))],
                    }
                }
            ],
        }
    ]

    _, figure = asyncio.run(
        render_plot_core(
            plot_data={},
            plot_properties={"xMin": 1, "xMax": 100, "yMin": -45, "yMax": -42},
            display_data_list=displays,
            output_format="object",
        )
    )

    try:
        figure.canvas.draw()
        # check there is only 1 sublot 
        assert len(figure.axes) == 1
        axes = figure.axes[0]
        # check that there is exactly one line being plotted
        assert len(axes.lines) == 1
        curve = axes.lines[0]
        # make sure the plotted points are close to the original points
        assert_allclose(curve.get_xdata(), masses)
        assert_allclose(curve.get_ydata(), cross_sections, atol=0)
        assert curve.get_color() == "black"
        assert axes.get_xscale() == "log"
        assert axes.get_yscale() == "log"
    finally:
        plt.close(figure)
