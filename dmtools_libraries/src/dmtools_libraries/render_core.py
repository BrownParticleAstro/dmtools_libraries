from typing import Any, Dict, List, Tuple
import base64
import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib import gridspec
from matplotlib.ticker import LogFormatterMathtext, LogLocator

from dmtools_libraries.helpers import get_style_mpl
from dmtools_libraries.helpers import convert_mass_units
from dmtools_libraries.helpers import get_x_label

async def render_plot_core(
    plot_data: Dict[str, Any],
    plot_properties: Dict[str, Any],
    display_data_list: List[Dict[str, Any]],
    figsize: Tuple[int, int] = (10, 10),
    output_format: str = "base64"  # "base64", "file", "object"
) -> Tuple[str, str]:
    """
    Context-agnostic plot renderer.

    Args:
        plot_data: The nested plot structure (passed in, not fetched)
        plot_properties: Plot config (xUnits, xMin, xMax, yMin, yMax, plotType, etc.)
        display_data_list: List of display dicts with style/color and data arrays
        figsize: Figure size tuple
        output_format: How to return the plot ("base64" for web, "file" for disk, "object" for Colab)

    Returns:
        (plot_name, plot_output) where plot_output depends on output_format
    """
    px = 1 / 100

    # Create figure
    #  fig = plt.figure(figsize=figsize, linewidth=0, edgecolor='#D0D6DB', facecolor='#D0D6DB')
    fig = plt.figure(figsize=figsize, linewidth=0, edgecolor="#FFFFFF", facecolor='#FFFFFF')
    gs = gridspec.GridSpec(64, 64)
    ax = fig.add_subplot(gs[2:63, 2:63])
    ax.set_facecolor('white')
  
    # ax.tick_params(axis='both', labelsize=16)

    ax.tick_params(axis='both', which='major', direction='in', top=True, right=True, length=9, width=1.5, labelsize=16)
    ax.tick_params(axis='both', which='minor', direction='in', top=True, right=True, length=5, width=1.1)


    plot_name = plot_properties.get('name', 'Plot')
    try:
        plot_id = plot_data.get("plot_node", {}).get("record", {}).get("id", -1)
    except:
        plot_id = -1
      

    # Iterate over displays and their data
    for display in display_data_list:
        display_properties = display.get('properties', {})
        style = display_properties.get('style', 'line')
        color = display_properties.get('color', 'black')

        # Get matplotlib kwargs from your style library
        line_plot_kwargs = get_style_mpl(color, style)
        line_plot_kwargs.pop('style', None)
        line_plot_kwargs.pop('fill', None)

        for data in display.get("data", []):
            data_properties = data.get('properties', {})

            y_rescale = float(data_properties.get('yRescale', 1))
            x_rescale = float(data_properties.get('xRescale', 1))
            x_units = data_properties.get('xUnits', 'GeV/c^2')

            trace_name = data_properties.get('label_short', 'Trace')
            list_data = data_properties.get('values', [[[0.0, 0.0], [0.0, 1.0]]])

            traces_xy = []  # NEW

            for trace in list_data:
                x = [float(item[0]) * x_rescale for item in trace]
                y = [float(item[1]) * y_rescale for item in trace]

                selected_unit = plot_properties.get('xUnits', 'GeV/c^2')
                plot_type = plot_properties.get('plotType')

                if plot_type == "Cross Section vs WIMP Mass":
                    unit_x = [convert_mass_units(val, x_units, selected_unit) for val in x]
                elif plot_type == "Cross Section / Mass [in GeV] vs Mass[GeV]":
                    unit_x = [convert_mass_units(val, x_units, 'GeV') for val in x]
                    y = [(float(item[1]) * y_rescale) / xi for item, xi in zip(trace, unit_x)]
                else:
                    unit_x = [convert_mass_units(val, x_units, selected_unit) for val in x]

                ax.plot(unit_x, y, **line_plot_kwargs)
                traces_xy.append((unit_x, y))  # NEW

                if style == 'fill' and len(list_data) != 2:  # CHANGED: two-trace case handled below
                    fill_plot_kwargs = get_style_mpl(color, style)
                    fill_plot_kwargs.pop('style', None)
                    fill_plot_kwargs.pop('marker', None)
                    fill_plot_kwargs.pop('markersize', None)
                    fill_plot_kwargs.pop('linestyle', None)
                    fill_plot_kwargs.pop('linewidth', None)
                    fill_plot_kwargs.pop('fill', None)
                    ax.fill_between(unit_x, y, **fill_plot_kwargs)

            # NEW: two traces with independent x lists -> closed polygon (trace 1 forward, trace 2 reversed)
            if style == 'fill' and len(list_data) == 2:
                fill_plot_kwargs = get_style_mpl(color, style)
                fill_plot_kwargs.pop('style', None)
                fill_plot_kwargs.pop('marker', None)
                fill_plot_kwargs.pop('markersize', None)
                fill_plot_kwargs.pop('linestyle', None)
                fill_plot_kwargs.pop('linewidth', None)
                fill_plot_kwargs.pop('fill', None)

                (x1, y1), (x2, y2) = traces_xy
                ax.fill(list(x1) + list(x2)[::-1], list(y1) + list(y2)[::-1], **fill_plot_kwargs)

    # Axes configuration
    ax.set_xscale('log')
    ax.set_yscale('log')

    ymin_exp = float(plot_properties.get('yMin', -42)) if plot_properties.get('yMin') else -42
    ymax_exp = float(plot_properties.get('yMax', -42)) if plot_properties.get('yMax') else -42
    xmin = float(plot_properties.get('xMin', 0)) if plot_properties.get('xMin') else 0
    xmax = float(plot_properties.get('xMax', 3)) if plot_properties.get('xMax') else 10000

    ax.set_xlim([xmin, xmax])
    ax.set_ylim([10**ymin_exp, 10**ymax_exp])

    # ax.set_ylabel(r"", fontsize=18)
    selected_unit = plot_properties.get('xUnits', 'GeV/c^2')
    # ax.set_xlabel(get_x_label(selected_unit), fontsize=18)

    ax.set_ylabel(r"$\mathrm{Cross\ Section}\ [\mathrm{cm}^{2}]$", fontsize=18)
    ax.set_xlabel(get_x_label(selected_unit), fontsize=18, labelpad=5)


    plot_title_default = r"$\mathrm{WIMP\ Mass\ vs\ Cross\ Section\ (Plot\ ID:\ " + str(plot_id) + r")}$"
    plot_title = plot_name + ' (' + str(plot_id) + ')' if plot_name else plot_title_default
    ax.set_title(plot_title, fontsize=18)

    # ax.xaxis.set_major_formatter(LogFormatterMathtext())
    # ax.yaxis.set_major_formatter(LogFormatterMathtext())

    ax.xaxis.set_major_locator(LogLocator(base=10))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1))
    ax.xaxis.set_major_formatter(LogFormatterMathtext())
    ax.yaxis.set_major_locator(LogLocator(base=10))
    ax.yaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1))
    ax.yaxis.set_major_formatter(LogFormatterMathtext())
  
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname('DejaVu Sans')
   
    for spine in ax.spines.values():
        spine.set_linewidth(1.4)

    # Output handling
    if output_format == "base64" or output_format == "web":
        img_svg = io.BytesIO()
        fig.savefig(img_svg, format='svg', dpi=100, bbox_inches='tight', pad_inches=0.2)
        img_svg.seek(0)
        plot_output = base64.b64encode(img_svg.getvalue()).decode('utf8')

        plot_output = f"/tmp/plot_{plot_id}.svg"
        img_svg = io.BytesIO()
        fig.savefig(img_svg, format='svg', dpi=100, bbox_inches='tight', pad_inches=0.2)
        plot_output_svg = base64.b64encode(img_svg.getvalue()).decode('utf8')
      
        plot_output = f"/tmp/plot_{plot_id}.pdf"
        img_pdf = io.BytesIO()
        fig.savefig(img_pdf, format='pdf', dpi=100, bbox_inches='tight', pad_inches=0.2)
        img_svg.seek(0)
        plot_output_pdf = base64.b64encode(img_pdf.getvalue()).decode('utf8')

        plt.close(fig)

        return (plot_name, plot_output_svg, plot_output_pdf)

    elif output_format == "object" or output_format == "notebook":
        # Return the matplotlib figure object (great for Colab display())
        plot_output = fig

        return (plot_name, plot_output)

    if output_format != "object":
        plt.close(fig)

    else:
        raise ValueError(f"Unknown output_format: {output_format}")


async def render_legend_core(display_data_list: List[Dict[str, Any]], output_type: str = "web"):
    """
    Pure legend renderer. This does not hit the DB or cache.
    """
    handles = []

    for display in display_data_list:
        display_properties = display.get("properties", {})
        style = display_properties.get("style", "line")
        color = display_properties.get("color", "black")

        for data in display.get("data", []):
            data_record = data.get("record", {})
            data_properties = data.get("properties", {})
            data_id = data_record.get("id", -1)

            trace_name = f"({data_id}):{data_properties.get('label_short', '')}"

            line_plot_kwargs = get_style_mpl(color, style)
            line_plot_kwargs.pop("style", None)
            line_plot_kwargs.pop("fill", None)

            fill_plot_kwargs = get_style_mpl(color, style)
            fill_plot_kwargs.pop("style", None)
            fill_plot_kwargs.pop("marker", None)
            fill_plot_kwargs.pop("markersize", None)

            if style != "fill":
                handle = mlines.Line2D([], [], label=trace_name, **line_plot_kwargs)
            else:
                handle = mpatches.Patch(label=trace_name, **fill_plot_kwargs)

            handles.append(handle)

    if not handles:
        fig, ax = plt.subplots(figsize=(6, 1.5), facecolor="white")
        ax.text(0.5, 0.5, "No legend", ha="center", va="center", fontsize=16)
        ax.axis("off")

        if output_type == "web":
            img_svg = io.BytesIO()
            fig.savefig(img_svg, format="svg", dpi=100, bbox_inches="tight", pad_inches=0.2)
            img_svg.seek(0)
            legend_output_svg = base64.b64encode(img_svg.getvalue()).decode("utf8")

            img_pdf = io.BytesIO()
            fig.savefig(img_pdf, format="pdf", dpi=100, bbox_inches="tight", pad_inches=0.2)
            img_pdf.seek(0)
            legend_output_pdf = base64.b64encode(img_pdf.getvalue()).decode("utf8")

            plt.close(fig)
            return (legend_output_svg, legend_output_pdf)

        elif output_type == "notebook":
            plot_output = fig
            plt.close(fig)
            return (plot_output)

        raise ValueError(f"Unknown output_type: {output_type}")

    labels = [handle.get_label() for handle in handles]

    fig, ax = plt.subplots(figsize=(10, 10), edgecolor="#FFFFFF", facecolor="#FFFFFF")
    legend = ax.legend(
        handles=handles,
        labels=labels,
        loc="upper center",
        fontsize=24,
        labelspacing=1,
        facecolor="white",
    )
    legend.get_frame().set_alpha(1)
    legend.get_frame().set_facecolor((1, 1, 1))
    ax.axis("off")

    if output_type == "web":
        img_svg = io.BytesIO()
        fig.savefig(img_svg, format="svg", dpi=100, bbox_inches="tight", pad_inches=0.2)
        img_svg.seek(0)
        legend_output_svg = base64.b64encode(img_svg.getvalue()).decode("utf8")

        img_pdf = io.BytesIO()
        fig.savefig(img_pdf, format="pdf", dpi=100, bbox_inches="tight", pad_inches=0.2)
        img_pdf.seek(0)
        legend_output_pdf = base64.b64encode(img_pdf.getvalue()).decode("utf8")

        plt.close(fig)
        return (legend_output_svg, legend_output_pdf)

    elif output_type == "notebook":
        plot_output = fig
        plt.close(fig)
        return (plot_output)

    else:
        plt.close(fig)
        raise ValueError(f"Unknown output_type: {output_type}")

