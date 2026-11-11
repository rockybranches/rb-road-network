"""Command-line client for the rb-road-network Worker.

The analysis runs in the Worker; these commands send it a start point (or a
CSV of sites), print the result and save the report files.

    rb-road-network status
    rb-road-network run --lat 33.732 --lon -84.4166 --name Atlanta
    rb-road-network batch --csv batch_inputs.csv
    rb-road-network batch --resume BATCH_ID

The Worker address comes from --url or RB_API_URL (default
http://localhost:8787, the local development server).
"""

import json
import re
import sys
from pathlib import Path

import click

from .client import DEFAULT_URL, URL_ENV, ApiError, Client

DEFAULT_OUTPUT_DIR = "output"


def _stem(label, fallback):
    """A file name stem from a site name; anything unusual becomes '_'."""
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", label or "").strip("._")
    return stem[:80] or fallback


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _save_outputs(client, record, tex_path):
    """Save the LaTeX table, the full result and the reachable area.

    The three files share a name: the given path plus .json and .geojson
    beside it. Returns the paths written.
    """
    aid = record["id"]
    paths = [tex_path, tex_path.with_suffix(".json"), tex_path.with_suffix(".geojson")]
    _write(paths[0], client.report_tex(aid))
    _write(paths[1], json.dumps(record, indent=2) + "\n")
    _write(paths[2], client.area_geojson(aid))
    return paths


def _people(n):
    return f"{n:,.0f}"


def _print_result(record):
    result = record["result"]
    report = result["report"]
    years = report["years"]
    reachable = result["reachable"]
    for warning in result["warnings"]:
        click.secho(f"Warning: {warning}", fg="yellow", err=True)
    if result["start"]["moved_to_nearest_road"]:
        click.echo(
            "Start point moved to the nearest road: "
            f"{result['start']['lat']}, {result['start']['lon']}"
        )

    rows = [
        [c["name"], c["state"]] + [_people(p) for p in c["population"]]
        for c in report["counties"]
    ]
    rows.append(["Total", ""] + [_people(t) for t in report["totals"]])
    header = ["County", "State"] + [str(y) for y in years]
    widths = [max(len(r[i]) for r in [header] + rows) for i in range(len(header))]

    def line(cells):
        left = [cells[0].ljust(widths[0]), cells[1].ljust(widths[1])]
        return "  ".join(left + [c.rjust(w) for c, w in zip(cells[2:], widths[2:])])

    click.echo()
    click.echo(line(header))
    click.echo("  ".join("-" * w for w in widths))
    for row in rows[:-1]:
        click.echo(line(row))
    click.echo("  ".join("-" * w for w in widths))
    click.echo(line(rows[-1]))
    click.echo()

    base, target = report["base_year"], report["target_year"]
    pct = report["percent_increase"]
    growth = f" ({pct:.1f}%)" if pct is not None else ""
    click.echo(f"Reachable area: {reachable['km2']:,.0f} km² in {len(report['counties'])} counties")
    click.echo(
        f"Population {base} to {target}: "
        f"{_people(report['population_increase'])} more people{growth}"
    )
    click.echo(
        f"Tons at {report['tons_per_person']:g} per person: "
        f"{_people(report['tons_base'])} in {base}, "
        f"{_people(report['tons_target'])} in {target}, "
        f"{_people(report['tons_increase'])} more"
    )
    missing = report["missing_population"]
    if missing:
        names = ", ".join(f"{c['name']}, {c['state']}" for c in missing)
        click.secho(
            f"Left out of the totals (no population figures): {names}",
            fg="yellow",
            err=True,
        )


@click.group()
@click.option(
    "--url",
    envvar=URL_ENV,
    default=DEFAULT_URL,
    show_default=True,
    help=f"Address of the Worker. Also read from {URL_ENV}.",
)
@click.pass_context
def cli(ctx, url):
    """Road-distance market area analysis.

    If the Worker is behind Cloudflare Access, put a service token in
    RB_ACCESS_CLIENT_ID and RB_ACCESS_CLIENT_SECRET.
    """
    ctx.obj = Client(url)


@cli.command()
@click.pass_obj
def status(client):
    """Show which datasets the Worker has loaded."""
    try:
        s = client.status()
    except ApiError as exc:
        raise click.ClickException(str(exc)) from None
    click.echo(f"Worker: {client.base_url}")
    click.echo(f"Roads dataset: {s['active']['roads']}")
    click.echo(f"Counties dataset: {s['active']['counties']}")
    for layer in s["raster_tiles"]:
        click.echo(f"  {layer['dataset']} / {layer['layer']}: {layer['tiles']:,} tiles")
    click.echo(
        f"Counties: {s['counties']:,} "
        f"({s['counties_with_population']:,} with population figures)"
    )


@cli.command()
@click.option("--lat", type=float, required=True, help="Latitude in decimal degrees.")
@click.option("--lon", type=float, required=True, help="Longitude in decimal degrees.")
@click.option(
    "-r", "--radius", type=float, default=75000, show_default=True,
    help="Distance by road, in metres.",
)  # fmt: skip
@click.option(
    "-t", "--tons-per-person", type=float, default=4.5, show_default=True,
    help="Tons per person.",
)  # fmt: skip
@click.option(
    "--min-km2", type=float, default=0, show_default=True,
    help="Leave out counties with less reachable area than this.",
)  # fmt: skip
@click.option("--name", default="", help="Name for the stored analysis.")
@click.option(
    "-f", "--output", type=click.Path(dir_okay=False, path_type=Path), default=None,
    help="Where to save the LaTeX table; the full result (.json) and the "
    "reachable area (.geojson) are saved beside it. "
    f"[default: {DEFAULT_OUTPUT_DIR}/<name or id>.tex]",
)  # fmt: skip
@click.pass_obj
def run(client, lat, lon, radius, tons_per_person, min_km2, name, output):
    """Analyse one start point and save the results."""
    try:
        record = client.create_analysis(
            {
                "lat": lat,
                "lon": lon,
                "radius_m": radius,
                "tons_per_person": tons_per_person,
                "min_km2": min_km2,
                "label": name,
            }
        )
        _print_result(record)
        if output is None:
            output = Path(DEFAULT_OUTPUT_DIR) / f"{_stem(name, record['id'])}.tex"
        paths = _save_outputs(client, record, output)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from None
    click.echo()
    click.echo("Saved: " + ", ".join(str(p) for p in paths))
    click.echo(f"Map: {client.page_url('#a/' + record['id'])}")


@cli.command()
@click.option(
    "--csv", "csv_file", type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Sites CSV with a header row: site, lat, lon.",
)  # fmt: skip
@click.option("--resume", "batch_id", help="Continue an existing batch by its id.")
@click.option("--name", default="", help="Name for the batch.")
@click.option(
    "-r", "--radius", type=float, default=75000, show_default=True,
    help="Distance by road, in metres.",
)  # fmt: skip
@click.option(
    "-t", "--tons-per-person", type=float, default=4.5, show_default=True,
    help="Tons per person.",
)  # fmt: skip
@click.option(
    "--min-km2", type=float, default=0, show_default=True,
    help="Leave out counties with less reachable area than this.",
)  # fmt: skip
@click.option(
    "-o", "--output-dir", type=click.Path(file_okay=False, path_type=Path),
    default=DEFAULT_OUTPUT_DIR, show_default=True,
    help="Directory for the summary CSV and the per-site files.",
)  # fmt: skip
@click.option(
    "--retry-failed", is_flag=True,
    help="With --resume, also run again the sites that failed.",
)  # fmt: skip
@click.pass_obj
def batch(client, csv_file, batch_id, name, radius, tons_per_person, min_km2,
          output_dir, retry_failed):  # fmt: skip
    """Analyse every site in a CSV.

    Finished sites are stored by the Worker as they complete, so an
    interrupted batch can be continued with --resume.
    """
    if (csv_file is None) == (batch_id is None):
        raise click.UsageError("give either --csv or --resume")
    try:
        if csv_file is not None:
            created = client.create_batch(
                {
                    "label": name or csv_file.stem,
                    "csv": csv_file.read_text(encoding="utf-8-sig"),
                    "radius_m": radius,
                    "tons_per_person": tons_per_person,
                    "min_km2": min_km2,
                }
            )
        else:
            created = client.batch(batch_id)
        batch_id = created["id"]
        sites = created["analyses"]
        click.echo(f"Batch {batch_id} ({created['label']}): {len(sites)} site(s)")
        click.echo(f"Map: {client.page_url('#b/' + batch_id)}")

        wanted = {"pending", "failed"} if retry_failed else {"pending"}
        failed = 0
        used = set()
        for n, site in enumerate(sites, start=1):
            label = site["request"]["label"] or f"site {n}"
            stem = _stem(site["request"]["label"], f"site_{n}")
            if stem in used:
                stem = f"{stem}_{n}"
            used.add(stem)
            if site["status"] in wanted:
                site = client.run_pending(site["id"])
            prefix = f"[{n}/{len(sites)}] {label}: "
            if site["status"] == "done":
                # The run and list responses carry only the summary; the
                # saved file gets the full result.
                _save_outputs(client, client.analysis(site["id"]), output_dir / f"{stem}.tex")
                s = site["summary"]
                click.echo(
                    f"{prefix}{s['counties']} counties, "
                    f"{_people(s['population_base'])} to "
                    f"{_people(s['population_target'])} people"
                )
            elif site["status"] == "failed":
                failed += 1
                click.secho(f"{prefix}failed: {site['error']}", fg="red", err=True)
            else:
                click.echo(f"{prefix}not run")

        summary_path = output_dir / f"batch_{batch_id}_summary.csv"
        _write(summary_path, client.batch_summary_csv(batch_id))
    except ApiError as exc:
        hint = f". Continue with: rb-road-network batch --resume {batch_id}" if batch_id else ""
        raise click.ClickException(f"{exc}{hint}") from None
    click.echo(f"Summary: {summary_path}")
    if failed:
        click.secho(f"{failed} site(s) failed.", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
