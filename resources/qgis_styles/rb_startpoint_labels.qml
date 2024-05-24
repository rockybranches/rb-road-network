<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.16.0-Hannover" simplifyMaxScale="1" maxScale="0" hasScaleBasedVisibilityFlag="0" simplifyAlgorithm="0" simplifyLocal="1" labelsEnabled="1" simplifyDrawingHints="0" styleCategories="AllStyleCategories" readOnly="0" minScale="100000000" simplifyDrawingTol="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal startExpression="" startField="" accumulate="0" durationField="" mode="0" endExpression="" durationUnit="min" fixedDuration="0" enabled="0" endField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 enableorderby="1" forceraster="0" symbollevels="0" type="singleSymbol">
    <symbols>
      <symbol name="0" alpha="1" force_rhr="0" clip_to_extent="1" type="marker">
        <layer pass="0" locked="0" class="SimpleMarker" enabled="1">
          <prop v="0" k="angle"/>
          <prop v="255,0,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="10" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="Point" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="enabled" type="Map">
                  <Option value="true" name="active" type="bool"/>
                  <Option value="name = 'StartPoint'" name="expression" type="QString"/>
                  <Option value="3" name="type" type="int"/>
                </Option>
              </Option>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer pass="0" locked="0" class="SimpleMarker" enabled="0">
          <prop v="0" k="angle"/>
          <prop v="34,165,225,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="2" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="enabled" type="Map">
                  <Option value="true" name="active" type="bool"/>
                  <Option value="name != 'StartPoint'" name="expression" type="QString"/>
                  <Option value="3" name="type" type="int"/>
                </Option>
              </Option>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
    <orderby>
      <orderByClause asc="1" nullsFirst="0">name = 'StartPoint'</orderByClause>
    </orderby>
  </renderer-v2>
  <labeling type="rule-based">
    <rules key="{2b7db0ef-e50d-4217-b498-9b4eb874d945}">
      <rule key="{15aac89e-e8e0-4d4e-bdcf-b1e6a499bfdc}" filter="name = 'StartPoint'">
        <settings calloutType="simple">
          <text-style isExpression="1" previewBkgrdColor="255,255,255,255" fontUnderline="1" fontKerning="1" namedStyle="Bold" fontSizeUnit="Point" fieldName="'Dickens-Hancock'" blendMode="0" multilineHeight="1" fontStrikeout="0" textOpacity="1" fontWeight="75" fontSize="24" fontWordSpacing="0" fontFamily="DejaVu Sans Ultra-Light" allowHtml="1" useSubstitutions="0" fontLetterSpacing="0" fontItalic="0" textColor="255,255,255,255" fontSizeMapUnitScale="3x:0,0,0,0,0,0" textOrientation="horizontal" capitalization="0">
            <text-buffer bufferDraw="0" bufferBlendMode="0" bufferSizeUnits="MM" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="255,255,255,255" bufferOpacity="1" bufferSize="1" bufferNoFill="0" bufferJoinStyle="128"/>
            <text-mask maskOpacity="1" maskEnabled="0" maskSizeUnits="MM" maskedSymbolLayers="" maskType="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskSize="1.5" maskJoinStyle="128"/>
            <background shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeSizeX="0" shapeBorderColor="0,0,0,255" shapeRotation="0" shapeSizeY="0" shapeOffsetX="0" shapeOffsetY="0" shapeBlendMode="0" shapeBorderWidth="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeType="0" shapeRadiiY="0" shapeDraw="1" shapeBorderWidthUnit="MM" shapeFillColor="0,0,0,255" shapeOpacity="1" shapeJoinStyle="64" shapeRadiiUnit="MM" shapeOffsetUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeRotationType="0" shapeSizeType="0" shapeSizeUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0">
              <symbol name="markerSymbol" alpha="1" force_rhr="0" clip_to_extent="1" type="marker">
                <layer pass="0" locked="0" class="SimpleMarker" enabled="1">
                  <prop v="0" k="angle"/>
                  <prop v="183,72,75,255" k="color"/>
                  <prop v="1" k="horizontal_anchor_point"/>
                  <prop v="bevel" k="joinstyle"/>
                  <prop v="circle" k="name"/>
                  <prop v="0,0" k="offset"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="35,35,35,255" k="outline_color"/>
                  <prop v="solid" k="outline_style"/>
                  <prop v="0" k="outline_width"/>
                  <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
                  <prop v="MM" k="outline_width_unit"/>
                  <prop v="diameter" k="scale_method"/>
                  <prop v="2" k="size"/>
                  <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
                  <prop v="MM" k="size_unit"/>
                  <prop v="1" k="vertical_anchor_point"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" name="name" type="QString"/>
                      <Option name="properties"/>
                      <Option value="collection" name="type" type="QString"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetGlobal="1" shadowOffsetUnit="MM" shadowOpacity="0.69999999999999996" shadowColor="0,0,0,255" shadowBlendMode="6" shadowScale="100" shadowRadius="1.5" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetAngle="135" shadowOffsetDist="1" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="3" reverseDirectionSymbol="0" formatNumbers="0" wrapChar="" decimals="3" addDirectionSymbol="0" autoWrapLength="0" leftDirectionSymbol="&lt;" useMaxLineLengthForAutoWrap="1" plussign="0" placeDirectionSymbol="0" rightDirectionSymbol=">"/>
          <placement layerType="PointGeometry" priority="5" distUnits="MM" overrunDistanceUnit="MM" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" fitInPolygonOnly="0" centroidWhole="0" overrunDistance="0" centroidInside="0" lineAnchorPercent="0.5" distMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" repeatDistance="0" placement="1" placementFlags="10" offsetUnits="MM" repeatDistanceUnits="MM" dist="5" geometryGenerator="" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" offsetType="0" maxCurvedCharAngleOut="-25" polygonPlacementFlags="2" rotationAngle="0" geometryGeneratorType="PointGeometry" lineAnchorType="0" xOffset="5" yOffset="-10" preserveRotation="1" quadOffset="4" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0"/>
          <rendering obstacleFactor="1" minFeatureSize="0" scaleMax="457631" fontMinPixelSize="3" obstacle="1" fontMaxPixelSize="10000" scaleMin="457631" displayAll="0" labelPerPart="0" maxNumLabels="2000" mergeLines="0" limitNumLabels="0" obstacleType="1" upsidedownLabels="0" zIndex="0" drawLabels="1" scaleVisibility="0" fontLimitPixelSize="0"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="IsObstacle" type="Map">
                  <Option value="false" name="active" type="bool"/>
                  <Option value="1" name="type" type="int"/>
                  <Option value="" name="val" type="QString"/>
                </Option>
                <Option name="PositionX" type="Map">
                  <Option value="true" name="active" type="bool"/>
                  <Option value="auxiliary_storage_labeling_positionx" name="field" type="QString"/>
                  <Option value="2" name="type" type="int"/>
                </Option>
                <Option name="PositionY" type="Map">
                  <Option value="true" name="active" type="bool"/>
                  <Option value="auxiliary_storage_labeling_positiony" name="field" type="QString"/>
                  <Option value="2" name="type" type="int"/>
                </Option>
              </Option>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" name="anchorPoint" type="QString"/>
              <Option name="ddProperties" type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties" type="Map">
                  <Option name="DrawCalloutToAllParts" type="Map">
                    <Option value="true" name="active" type="bool"/>
                    <Option value="name='StartPoint'" name="expression" type="QString"/>
                    <Option value="3" name="type" type="int"/>
                  </Option>
                </Option>
                <Option value="collection" name="type" type="QString"/>
              </Option>
              <Option value="true" name="drawToAllParts" type="bool"/>
              <Option value="1" name="enabled" type="QString"/>
              <Option value="centroid" name="labelAnchorPoint" type="QString"/>
              <Option value="&lt;symbol name=&quot;symbol&quot; alpha=&quot;1&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; type=&quot;line&quot;>&lt;layer pass=&quot;0&quot; locked=&quot;0&quot; class=&quot;ArrowLine&quot; enabled=&quot;1&quot;>&lt;prop v=&quot;1&quot; k=&quot;arrow_start_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;arrow_start_width_unit&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;arrow_start_width_unit_scale&quot;/>&lt;prop v=&quot;0&quot; k=&quot;arrow_type&quot;/>&lt;prop v=&quot;1&quot; k=&quot;arrow_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;arrow_width_unit&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;arrow_width_unit_scale&quot;/>&lt;prop v=&quot;1.5&quot; k=&quot;head_length&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;head_length_unit&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;head_length_unit_scale&quot;/>&lt;prop v=&quot;1.5&quot; k=&quot;head_thickness&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;head_thickness_unit&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;head_thickness_unit_scale&quot;/>&lt;prop v=&quot;0&quot; k=&quot;head_type&quot;/>&lt;prop v=&quot;1&quot; k=&quot;is_curved&quot;/>&lt;prop v=&quot;1&quot; k=&quot;is_repeated&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;Point&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_unit_scale&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; name=&quot;name&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; name=&quot;type&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;symbol name=&quot;@symbol@0&quot; alpha=&quot;1&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; type=&quot;fill&quot;>&lt;layer pass=&quot;0&quot; locked=&quot;0&quot; class=&quot;SimpleFill&quot; enabled=&quot;1&quot;>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;border_width_map_unit_scale&quot;/>&lt;prop v=&quot;0,0,0,255&quot; k=&quot;color&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;0,0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;Point&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0,0,0,255&quot; k=&quot;outline_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;outline_style&quot;/>&lt;prop v=&quot;2&quot; k=&quot;outline_width&quot;/>&lt;prop v=&quot;Point&quot; k=&quot;outline_width_unit&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;style&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; name=&quot;name&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; name=&quot;type&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>&lt;/layer>&lt;/symbol>" name="lineSymbol" type="QString"/>
              <Option value="5.551115123125783e-17" name="minLength" type="double"/>
              <Option value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale" type="QString"/>
              <Option value="MM" name="minLengthUnit" type="QString"/>
              <Option value="0" name="offsetFromAnchor" type="double"/>
              <Option value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale" type="QString"/>
              <Option value="MM" name="offsetFromAnchorUnit" type="QString"/>
              <Option value="0" name="offsetFromLabel" type="double"/>
              <Option value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale" type="QString"/>
              <Option value="MM" name="offsetFromLabelUnit" type="QString"/>
            </Option>
          </callout>
        </settings>
      </rule>
    </rules>
  </labeling>
  <customproperties>
    <property key="dualview/previewExpressions" value="&quot;name&quot;"/>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory sizeType="MM" height="15" maxScaleDenominator="1e+08" width="15" lineSizeType="MM" showAxis="1" rotationOffset="270" direction="0" penColor="#000000" scaleBasedVisibility="0" spacingUnitScale="3x:0,0,0,0,0,0" enabled="0" lineSizeScale="3x:0,0,0,0,0,0" diagramOrientation="Up" barWidth="5" penAlpha="255" sizeScale="3x:0,0,0,0,0,0" backgroundColor="#ffffff" spacing="5" opacity="1" scaleDependency="Area" backgroundAlpha="255" spacingUnit="MM" minScaleDenominator="0" penWidth="0" labelPlacementMethod="XHeight" minimumSize="0">
      <fontProperties description="DejaVu Sans Ultra-Light,12,-1,5,50,0,0,0,0,0" style=""/>
      <attribute label="" color="#000000" field=""/>
      <axisSymbol>
        <symbol name="" alpha="1" force_rhr="0" clip_to_extent="1" type="line">
          <layer pass="0" locked="0" class="SimpleLine" enabled="1">
            <prop v="0" k="align_dash_pattern"/>
            <prop v="square" k="capstyle"/>
            <prop v="5;2" k="customdash"/>
            <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
            <prop v="MM" k="customdash_unit"/>
            <prop v="0" k="dash_pattern_offset"/>
            <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
            <prop v="MM" k="dash_pattern_offset_unit"/>
            <prop v="0" k="draw_inside_polygon"/>
            <prop v="bevel" k="joinstyle"/>
            <prop v="35,35,35,255" k="line_color"/>
            <prop v="solid" k="line_style"/>
            <prop v="0.26" k="line_width"/>
            <prop v="MM" k="line_width_unit"/>
            <prop v="0" k="offset"/>
            <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
            <prop v="MM" k="offset_unit"/>
            <prop v="0" k="ring_filter"/>
            <prop v="0" k="tweak_dash_pattern_on_corners"/>
            <prop v="0" k="use_custom_dash"/>
            <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings placement="0" linePlacementFlags="18" zIndex="0" showAll="1" dist="0" priority="0" obstacle="0">
    <properties>
      <Option type="Map">
        <Option value="" name="name" type="QString"/>
        <Option name="properties"/>
        <Option value="collection" name="type" type="QString"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="marker-color" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="marker-size" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="marker-symbol" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="name" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" name="" field="marker-color"/>
    <alias index="1" name="" field="marker-size"/>
    <alias index="2" name="" field="marker-symbol"/>
    <alias index="3" name="" field="name"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" field="marker-color" expression=""/>
    <default applyOnUpdate="0" field="marker-size" expression=""/>
    <default applyOnUpdate="0" field="marker-symbol" expression=""/>
    <default applyOnUpdate="0" field="name" expression=""/>
  </defaults>
  <constraints>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="marker-color" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="marker-size" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="marker-symbol" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="name" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" field="marker-color" exp=""/>
    <constraint desc="" field="marker-size" exp=""/>
    <constraint desc="" field="marker-symbol" exp=""/>
    <constraint desc="" field="name" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" name="marker-color" hidden="0" type="field"/>
      <column width="-1" name="marker-size" hidden="0" type="field"/>
      <column width="-1" name="marker-symbol" hidden="0" type="field"/>
      <column width="-1" name="name" hidden="0" type="field"/>
      <column width="-1" hidden="1" type="actions"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="auxiliary_storage_labeling_positionx" editable="0"/>
    <field name="auxiliary_storage_labeling_positiony" editable="0"/>
    <field name="marker-color" editable="1"/>
    <field name="marker-size" editable="1"/>
    <field name="marker-symbol" editable="1"/>
    <field name="name" editable="1"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="auxiliary_storage_labeling_positionx"/>
    <field labelOnTop="0" name="auxiliary_storage_labeling_positiony"/>
    <field labelOnTop="0" name="marker-color"/>
    <field labelOnTop="0" name="marker-size"/>
    <field labelOnTop="0" name="marker-symbol"/>
    <field labelOnTop="0" name="name"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"name"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
