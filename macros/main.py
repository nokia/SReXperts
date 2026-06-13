# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

"""
Mkdocs-macros module
"""

import posixpath


def _normalize_path(path, env):
    """Turn a path relative to the current markdown file into a URL relative to the built HTML.

    With ``use_directory_urls``, ``page.md`` becomes ``page/index.html`` while
    ``section/index.md`` stays ``section/index.html``.  Raw HTML in macros is not
    rewritten like Markdown image URLs, so the correct relative URL must be derived
    from ``File.dest_path`` for the page and the asset.
    """
    if not path:
        return path
    if path.startswith(("http://", "https://", "/", "#")):
        return path

    page_file = env.page.file
    page_src_dir = posixpath.dirname(page_file.src_path)
    resolved_src = posixpath.normpath(posixpath.join(page_src_dir, path))
    # mkdocs-macros attaches MkDocs' Files collection in on_nav (see plugin on_nav).
    try:
        files = env.variables["files"]
    except (TypeError, KeyError, AttributeError):
        files = None
    if files is None:
        return path
    asset = files.get_file_from_path(resolved_src)
    if asset is None:
        return path
    page_dest_dir = posixpath.dirname(page_file.dest_path) or "."
    rel = posixpath.relpath(asset.dest_path, page_dest_dir)

    return rel.replace("\\", "/")


def _scale_to_width_percent(scale):
    """Return a CSS width percentage from a numeric scale factor, or None.

    ``scale`` is a multiplier on the container width: ``0.5`` → ``50%``,
    ``2`` → ``200%``. ``1`` means natural layout (no width style). Empty
    string is treated like the default. Only ``int``/``float`` are accepted
    (booleans and other types are ignored).
    """
    if scale is None or scale == "":
        return None
    if isinstance(scale, bool):
        return None
    if not isinstance(scale, (int, float)):
        return None
    if scale <= 0:
        return None
    if scale == 1:
        return None
    pct = scale * 100.0
    if pct.is_integer():
        return f"{int(pct)}%"
    return f"{pct:g}%"


def define_env(env):
    """
    Macroses used in SR Linux documentation
    """

    @env.macro
    def diagram(url="", path="", page=0, title="", zoom=2):
        """
        Diagram macro. URL can be a local file `path` that starts with a ./ (dot) or ../ (dot-dot) prefix
        or a remote URL `url` that starts with http or https or a shorthand syntax for drawio files kept in a GitHub repo.
        """

        _location = ""

        # to allow shorthand syntax for drawio URLs, like:
        # srl-labs/srlinux-getting-started/main/diagrams/topology.drawio
        # we will append the missing prefix to it if it doesn't start with http already
        if not url.startswith("http"):
            _location = "https://raw.githubusercontent.com/" + url

        if path:
            _location = _normalize_path(path, env)

        diagram_tmpl = f"""
<figure>
    <div class='mxgraph'
            style='max-width:100%;border:1px solid transparent;margin:0 auto; display:block; box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1); border-radius: 0.25rem;'
            data-mxgraph='{{"url":"{_location}","page":{page},"zoom":{zoom},"highlight":"#0000ff","nav":true,"resize":true,"edit":"_blank","dark-mode":false}}'>
    </div>
    {f"<figcaption>{title}</figcaption>" if title else ""}
</figure>
"""

        return diagram_tmpl

    @env.macro
    def video(url, title=""):
        """
        HTML5 video macro
        """

        video_tmpl = f"""
<figure>
<video style="overflow: hidden; box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1); border-radius: 0.25rem;" width="100%" controls playsinline>
    <source src="{url}" type="video/mp4">
</video>
{f"<figcaption>{title}</figcaption>" if title else ""}
</figure>
"""

        return video_tmpl

    @env.macro
    def youtube(url):
        """
        Youtube video macro
        """

        video_tmpl = f"""
<div class="iframe-container" >
<iframe style="box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1); border-radius: 0.25rem;" src="{url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>
"""

        return video_tmpl

    @env.macro
    def image(
        url="",
        light_url="",
        dark_url="",
        padding=0,
        border_radius=0.0,
        shadow=False,
        center=True,
        scale=1,
        title="",
        id="",
    ):
        """
        Image macro with dot background.

        Parameters:
            url (str): Image URL. Used for both light and dark modes if no specific URLs are provided.
            light_url (str): Image URL for light mode.
            dark_url (str): Image URL for dark mode.
            padding (int): Padding around the image (in px). Default is 0.
            border_radius (float): Border radius for the image (in rem). Default is 0.0.
            shadow (bool): Whether to apply a shadow to the image. Default is False.
            center (bool): Whether to center the image in the figure. Default is True.
            scale (int | float): Width as a multiple of the container width: ``1`` is default
                (no extra width; natural size). ``0.5`` is half, ``2`` is double. Non-numeric
                values, non-positive values, and ``1`` apply no width override.
            title (str): Optional caption/title for the image. Default is "".
            id (str): Optional ID for the image. Default is "".
        """
        url = _normalize_path(url, env)
        light_url = _normalize_path(light_url, env)
        dark_url = _normalize_path(dark_url, env)

        scale_width = _scale_to_width_percent(scale)
        img_scale_style = (
            f' style="width: {scale_width}; height: auto;"' if scale_width else ""
        )

        if shadow:
            img_class = "img-shadow"
        else:
            img_class = ""

        # if only one url is provided the image is used for both light and dark modes
        img_src = (
            f'<img src="{url}" class="{img_class}"{img_scale_style} alt="{title}">'
        )

        # if light and dark url are provided
        if light_url and dark_url:
            img_src = (
                f'<img src="{light_url}#only-light" class="{img_class}"{img_scale_style} alt="{title}">'
                f'<img src="{dark_url}#only-dark" class="{img_class}"{img_scale_style} alt="{title}">'
            )

        # Compute base style
        base_style = f"border-radius: {border_radius}rem; position: relative; display: inline-block;"
        if center:
            center_style = "text-align: center; width: 100%;"
        else:
            center_style = ""
        div_style = f"padding: {padding}px; {base_style} {center_style}".strip()
        # remove bottom padding when figure is used since figcaption adds its own spacing
        figure_style = f"padding: {padding}px {padding}px 0 {padding}px; {base_style} {center_style}".strip()

        # if title is provided, use figure element with figcaption inside the polka div
        if title:
            image_tmpl = (
                f'<figure class="polka" style="{figure_style}" id="{id}">{img_src}'
                f"<figcaption>{title}</figcaption></figure>"
            )
        else:
            image_tmpl = f'<div class="polka" style="{div_style}" id="{id}">{img_src}</div>'

        return image_tmpl
