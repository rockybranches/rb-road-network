#!/usr/bin/env python3
"""
Concatenate multiple shapefiles into a single shapefile using GDAL/OGR.

This script provides a high-performance Python equivalent to the bash ogr2ogr_concat_shpfiles
script. It uses the GDAL Python bindings directly to avoid subprocess overhead.

Usage:
    ogr2ogr_concat_shpfiles.py [input] [output_dir] [output_filename] [layer_name]

Examples:
    ogr2ogr_concat_shpfiles.py
    ogr2ogr_concat_shpfiles.py /path/to/input.shp /output/dir output.shp output_layer
"""

import os
import sys
import click
from pathlib import Path
from osgeo import ogr, osr


class Config:
    """Global configuration."""
    def __init__(self):
        self.verbose = False
        self.feature_count = 0
        self.file_count = 0


def copy_shapefile(src_path, dst_path, config, overwrite=False):
    """
    Copy a shapefile from source to destination.
    
    Args:
        src_path: Source shapefile path
        dst_path: Destination shapefile path
        config: Global configuration object
        overwrite: Whether to overwrite existing files
    """
    # Check if output file exists
    if Path(dst_path).exists() and not overwrite:
        if not click.confirm(f"Output file {dst_path} already exists. Overwrite?"):
            raise click.Abort()
    
    src_ds = ogr.Open(src_path)
    if not src_ds:
        raise IOError(f"Failed to open source shapefile: {src_path}")
    
    try:
        src_layer = src_ds.GetLayer(0)
        driver = ogr.GetDriverByName("ESRI Shapefile")
        
        # Create output dataset
        dst_ds = driver.CreateDataSource(dst_path)
        if not dst_ds:
            raise IOError(f"Failed to create output shapefile: {dst_path}")
        
        # Get spatial reference
        spatial_ref = src_layer.GetSpatialRef()
        
        # Create layer with same geometry type
        dst_layer = dst_ds.CreateLayer(
            src_layer.GetName(),
            geom_type=src_layer.GetGeomType(),
            srs=spatial_ref
        )
        
        # Copy field definitions
        layer_def = src_layer.GetLayerDefn()
        for i in range(layer_def.GetFieldCount()):
            field_def = layer_def.GetFieldDefn(i)
            dst_layer.CreateField(field_def)
        
        # Count and copy features with progress bar
        feature_count = src_layer.GetFeatureCount()
        if config.verbose:
            click.echo(f"  Copying {feature_count:,} features...")
        
        dst_layer_def = dst_layer.GetLayerDefn()
        src_layer.ResetReading()
        
        for idx, src_feature in enumerate(src_layer):
            dst_feature = ogr.Feature(dst_layer_def)
            dst_feature.SetGeometry(src_feature.GetGeometryRef().Clone())
            
            for i in range(dst_layer_def.GetFieldCount()):
                dst_feature.SetField(i, src_feature.GetField(i))
            
            dst_layer.CreateFeature(dst_feature)
            config.feature_count += 1
        
        dst_ds.SyncToDisk()
        dst_ds = None
        click.secho(f"✓ Created output shapefile with {feature_count:,} features", fg='green')
        
    finally:
        src_ds = None


def append_shapefiles(output_path, input_dir, layer_name, config):
    """
    Append shapefiles from subdirectories to the output shapefile.
    
    Args:
        output_path: Path to the output shapefile
        input_dir: Directory to search for shapefiles
        layer_name: Name of the layer to append to
        config: Global configuration object
    """
    output_ds = ogr.Open(output_path, update=True)
    if not output_ds:
        raise IOError(f"Failed to open output shapefile for update: {output_path}")
    
    try:
        output_layer = output_ds.GetLayer(0)
        output_layer_def = output_layer.GetLayerDefn()
        
        # Search for all .shp files in subdirectories
        input_path = Path(input_dir)
        shp_files = sorted([f for f in input_path.rglob("*.shp")])
        
        if not shp_files:
            click.secho(f"⚠ No shapefiles found in {input_dir}", fg='yellow')
            return
        
        click.echo(f"Found {len(shp_files)} shapefile(s) to append")
        
        for idx, shp_file in enumerate(shp_files, 1):
            src_ds = ogr.Open(str(shp_file))
            if not src_ds:
                click.secho(f"✗ Failed to open {shp_file.name}", fg='red')
                continue
            
            try:
                src_layer = src_ds.GetLayer(0)
                feature_count = src_layer.GetFeatureCount()
                
                if config.verbose:
                    click.echo(f"  [{idx}/{len(shp_files)}] Processing {shp_file.name} ({feature_count:,} features)...", nl=False)
                
                # Append features
                src_layer.ResetReading()
                for src_feature in src_layer:
                    dst_feature = ogr.Feature(output_layer_def)
                    dst_feature.SetGeometry(src_feature.GetGeometryRef().Clone())
                    
                    # Copy all field values
                    for i in range(output_layer_def.GetFieldCount()):
                        field_def = output_layer_def.GetFieldDefn(i)
                        field_name = field_def.GetName()
                        try:
                            dst_feature.SetField(field_name, src_feature.GetField(field_name))
                        except (ValueError, RuntimeError):
                            # Field doesn't exist in source, skip
                            pass
                    
                    output_layer.CreateFeature(dst_feature)
                    config.feature_count += 1
                
                config.file_count += 1
                click.secho(f" ✓", fg='green')
                
            except Exception as e:
                click.secho(f" ✗ Error: {e}", fg='red')
                
            finally:
                src_ds = None
        
        output_ds.SyncToDisk()
        
    finally:
        output_ds = None



def get_default_input():
    """Get default input path from RB_DATA environment variable."""
    rb_data = os.environ.get("RB_DATA", "/data/rb_data")
    return f"{rb_data}/gis_osm_roads_extra/georgia_geom"


def get_default_output_dir():
    """Get default output directory from RB_DATA environment variable."""
    rb_data = os.environ.get("RB_DATA", "/data/rb_data")
    return f"{rb_data}/gis_osm_roads/gis_osm_roads_free_1.shp"


@click.command()
@click.argument('input', default=get_default_input(), type=click.Path(exists=False))
@click.argument('output_dir', default=get_default_output_dir(), type=click.Path())
@click.argument('output_filename', default='gis_osm_roads_free_1.shp')
@click.argument('layer_name', default='gis_osm_roads_free_1')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose output')
@click.option('-f', '--force', is_flag=True, help='Overwrite output files without confirmation')
@click.pass_context
def main(ctx, input, output_dir, output_filename, layer_name, verbose, force):
    """Concatenate multiple shapefiles into a single shapefile.
    
    \b
    Default values use the $RB_DATA environment variable:
    - INPUT: $RB_DATA/gis_osm_roads/gis_osm_roads_free_1.shp
    - OUTPUT_DIR: $RB_DATA/gis_osm_roads_extra/georgia_geom
    
    \b
    Examples:
      ogr2ogr_concat_shpfiles.py
      ogr2ogr_concat_shpfiles.py /path/to/input.shp /output/dir output.shp layer_name
      ogr2ogr_concat_shpfiles.py --force --verbose
    """
    config = Config()
    config.verbose = verbose
    
    # Validate paths
    if not os.path.exists(input):
        click.secho(f"✗ Error: Input file not found: {input}", fg='red', err=True)
        sys.exit(1)
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        # Display header
        click.secho("\n" + "="*60, fg='blue')
        click.secho("Shapefile Concatenation Tool", fg='blue', bold=True)
        click.secho("="*60 + "\n", fg='blue')
        
        # Show configuration
        if verbose:
            click.echo("Configuration:")
            click.echo(f"  Input: {input}")
            click.echo(f"  Output Dir: {output_dir}")
            click.echo(f"  Output File: {output_filename}")
            click.echo(f"  Layer Name: {layer_name}")
            click.echo()
        
        # Step 1: Copy initial shapefile
        click.echo("Step 1: Copying initial shapefile...")
        copy_shapefile(input, output_path, config, overwrite=force)
        
        # Step 2: Append additional shapefiles
        click.echo("\nStep 2: Appending additional shapefiles...")
        append_shapefiles(output_path, output_dir, layer_name, config)
        
        # Summary
        click.secho("\n" + "="*60, fg='blue')
        click.secho("Summary", fg='blue', bold=True)
        click.secho("="*60, fg='blue')
        click.secho(f"✓ Total features processed: {config.feature_count:,}", fg='green')
        click.secho(f"✓ Total files appended: {config.file_count}", fg='green')
        click.secho(f"✓ Output file: {output_path}\n", fg='green')
        
    except click.Abort():
        click.secho("\n✗ Operation cancelled by user", fg='yellow')
        sys.exit(0)
    except Exception as e:
        click.secho(f"\n✗ Error: {e}", fg='red', err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
