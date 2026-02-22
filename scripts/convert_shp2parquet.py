#!/usr/bin/env python3
"""
Convert shapefile (.shp) to Parquet format.

This script converts ESRI shapefiles to Apache Parquet format using geopandas.
The geometry is preserved as binary (WKB) in the Parquet file.

Usage:
    convert_shp2parquet.py [input] [output] [options]

Examples:
    convert_shp2parquet.py input.shp output.parquet
    convert_shp2parquet.py /path/to/roads.shp /path/to/roads.parquet --compression snappy
"""

import os
import sys
import click
from pathlib import Path

import geopandas as gpd


@click.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.argument("output", type=click.Path(path_type=Path))
@click.option(
    "-c",
    "--compression",
    type=click.Choice(["snappy", "gzip", "brotli", "none"]),
    default="snappy",
    help="Compression codec for Parquet file (default: snappy)",
)
@click.option(
    "-f", "--force", is_flag=True, help="Overwrite output file without confirmation"
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def main(ctx, input, output, compression, force, verbose):
    """Convert a shapefile to Parquet format.

    INPUT: Path to the input shapefile (.shp)
    OUTPUT: Path to the output Parquet file (.parquet)
    """
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        click.secho(
            f"✗ Error: Could not create output directory: {e}", fg="red", err=True
        )
        sys.exit(1)

    if output.exists() and not force:
        if not click.confirm(f"Output file {output} already exists. Overwrite?"):
            click.secho("Cancelled", fg="yellow")
            sys.exit(0)

    compression_opt = None if compression == "none" else compression

    try:
        click.secho("\n" + "=" * 60, fg="blue")
        click.secho("Shapefile to Parquet Converter", fg="blue", bold=True)
        click.secho("=" * 60 + "\n", fg="blue")

        if verbose:
            click.echo(f"Input:    {input}")
            click.echo(f"Output:   {output}")
            click.echo(f"Compression: {compression}")
            click.echo()

        click.echo("Reading shapefile...")
        gdf = gpd.read_file(input)

        feature_count = len(gdf)
        click.echo(f"  Found {feature_count:,} features")

        if verbose:
            click.echo("\nColumns:")
            for col in gdf.columns:
                click.echo(f"  - {col}: {gdf[col].dtype}")
            click.echo(f"\nGeometry type: {gdf.geom_type.iloc[0]}")
            click.echo(f"CRS: {gdf.crs}")

        click.echo("\nWriting Parquet file...")

        gdf.to_parquet(
            output, compression=compression_opt, engine="pyarrow", index=False
        )

        output_size = output.stat().st_size
        click.secho(f"✓ Created {output} ({output_size:,} bytes)", fg="green")
        click.secho(f"✓ Converted {feature_count:,} features\n", fg="green")

    except click.Abort():
        click.secho("\n✗ Operation cancelled", fg="yellow")
        sys.exit(0)
    except Exception as e:
        click.secho(f"\n✗ Error: {e}", fg="red", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
