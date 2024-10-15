import unittest
import xml.etree.ElementTree as ET

from evedata.scan.boundaries.scan import Scan
from evedata.scan.boundaries.scml import SCML
from evedata.scan.controllers import version_mapping
from evedata.scan.entities import scan


SCML_STRING = """<?xml version="1.0" encoding="UTF-8"?>
<tns:scml xsi:schemaLocation="http://www.ptb.de/epics/SCML scml.xsd"
    xmlns:tns="http://www.ptb.de/epics/SCML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <location>TEST</location>
    <version>9.2</version>
    <scan>
        <repeatcount>0</repeatcount>
        <comment>test ccd time</comment>
        <savefilename>/messung/test/daten/2024/kw${WEEK}/interval-detector-test-</savefilename>
        <confirmsave>false</confirmsave>
        <autonumber>true</autonumber>
        <savescandescription>true</savescandescription>
        <chain id="1">
            <pauseconditions/>
            <scanmodules>
                <scanmodule id="15">
                    <name>Dynamic Axis Snapshot</name>
                    <xpos>90</xpos>
                    <ypos>83</ypos>
                    <parent>0</parent>
                    <appended>1</appended>
                    <dynamic_axis_positions/>
                </scanmodule>
                <scanmodule id="1">
                    <name>SM 1</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>15</parent>
                    <nested>2</nested>
                    <appended>3</appended>
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
                        <prescan>
                            <id>SimMt:testrack01000.LLM</id>
                            <value type="double">30</value>
                        </prescan>
                        <smaxis>
                            <axisid>Timer1-mot-double</axisid>
                            <stepfunction>Add</stepfunction>
                            <positionmode>absolute</positionmode>
                            <startstopstep>
                                <start type="double">1.0</start>
                                <stop type="double">5.0</stop>
                                <stepwidth type="double">1.0</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>
                        <smchannel>
                            <channelid>mlsCurrent:Mnt1chan1</channelid>
                            <interval>
                                <triggerinterval>0.01</triggerinterval>
                                <stoppedby>Timer1-det-double</stoppedby>
                            </interval>
                        </smchannel>
                        <smchannel>
                            <channelid>Timer1-det-double</channelid>
                            <standard>
                                <averagecount>500</averagecount>
                                <sendreadyevent>true</sendreadyevent>
                            </standard>
                        </smchannel>
                        <postscan>
                            <id>SimMt:testrack01000.LLM</id>
                            <reset_originalvalue>true</reset_originalvalue>
                        </postscan>
                    </classic>
                </scanmodule>
                <scanmodule id="2">
                    <name>SM 1</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>1</parent>
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
                        <prescan>
                            <id>SimMt:testrack01000.LLM</id>
                            <value type="double">30</value>
                        </prescan>
                        <prescan>
                            <id>K0617:gw24126.SCAN</id>
                            <value type="string">Passive</value>
                        </prescan>
                        <smaxis>
                            <axisid>Timer1-mot-double</axisid>
                            <stepfunction>Add</stepfunction>
                            <positionmode>absolute</positionmode>
                            <startstopstep>
                                <start type="double">1.0</start>
                                <stop type="double">5.0</stop>
                                <stepwidth type="double">1.0</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>
                        <smchannel>
                            <channelid>mlsCurrent:Mnt1chan1</channelid>
                            <interval>
                                <triggerinterval>0.01</triggerinterval>
                                <stoppedby>Timer1-det-double</stoppedby>
                            </interval>
                        </smchannel>
                        <smchannel>
                            <channelid>Timer1-det-double</channelid>
                            <standard>
                                <averagecount>500</averagecount>
                                <sendreadyevent>true</sendreadyevent>
                            </standard>
                        </smchannel>
                        <postscan>
                            <id>SimMt:testrack01000.LLM</id>
                            <reset_originalvalue>true</reset_originalvalue>
                        </postscan>
                        <postscan>
                            <id>K0617:gw24126.SCAN</id>
                            <value type="string">.5 second</value>
                        </postscan>
                    </classic>
                </scanmodule>
                <scanmodule id="3">
                    <name>Static Axis Snapshot</name>
                    <xpos>147</xpos>
                    <ypos>57</ypos>
                    <parent>2</parent>
                    <appended>4</appended>
                    <save_axis_positions>
                        <smaxis>
                            <axisid>DiscPosSimMt:testrack01000</axisid>
                            <stepfunction>Plugin</stepfunction>
                            <positionmode>absolute</positionmode>
                            <plugin name="MotionDisabled">
                                <parameter name="location">/path/to/referenceadd</parameter>
                            </plugin>
                        </smaxis>
                    </save_axis_positions>
                </scanmodule>
                <scanmodule id="4">
                    <name>Static Channel Snapshot</name>
                    <xpos>333</xpos>
                    <ypos>77</ypos>
                    <parent>3</parent>
                    <save_channel_values>
                        <smchannel>
                            <channelid>SmCounter-det</channelid>
                            <standard/>
                        </smchannel>
                        <smchannel>
                            <channelid>bIICurrent:Mnt1chan1</channelid>
                            <standard/>
                        </smchannel>
                    </save_channel_values>
                </scanmodule>
                <scanmodule id="42">
                    <name>Not connected scan module</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>-1</parent>
                    <appended>43</appended>
                    <nested>44</nested>
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
                        <smaxis>
                            <axisid>Timer1-mot-double</axisid>
                            <stepfunction>Add</stepfunction>
                            <positionmode>absolute</positionmode>
                            <startstopstep>
                                <start type="double">1.0</start>
                                <stop type="double">5.0</stop>
                                <stepwidth type="double">1.0</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>
                    </classic>
                </scanmodule>
                <scanmodule id="43">
                    <name>Not connected scan module</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>42</parent>
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
                        <smaxis>
                            <axisid>Timer1-mot-double</axisid>
                            <stepfunction>Add</stepfunction>
                            <positionmode>absolute</positionmode>
                            <startstopstep>
                                <start type="double">1.0</start>
                                <stop type="double">5.0</stop>
                                <stepwidth type="double">1.0</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>
                    </classic>
                </scanmodule>
                <scanmodule id="44">
                    <name>Not connected scan module</name>
                    <xpos>228</xpos>
                    <ypos>124</ypos>
                    <parent>42</parent>
                    <classic>
                        <valuecount>1</valuecount>
                        <settletime>0.0</settletime>
                        <triggerdelay>0.0</triggerdelay>
                        <triggerconfirmaxis>false</triggerconfirmaxis>
                        <triggerconfirmchannel>false</triggerconfirmchannel>
                        <smaxis>
                            <axisid>Timer1-mot-double</axisid>
                            <stepfunction>Add</stepfunction>
                            <positionmode>absolute</positionmode>
                            <startstopstep>
                                <start type="double">1.0</start>
                                <stop type="double">5.0</stop>
                                <stepwidth type="double">1.0</stepwidth>
                                <ismainaxis>false</ismainaxis>
                            </startstopstep>
                        </smaxis>
                    </classic>
                </scanmodule>
            </scanmodules>
        </chain>
        <monitoroptions type="none"/>
    </scan>
    <plugins/>
    <detectors>
        <detector>
            <class>Timer</class>
            <name>detSecTime</name>
            <id>detSecTime</id>
            <channel>
                <class></class>
                <name>Time</name>
                <id>Timer1-det-double</id>
                <read>
                    <access method="GETCB" type="double" transport="local">Timer</access>
                </read>
            </channel>
        </detector>
    </detectors>
    <motors>
        <motor>
            <class>Timer</class>
            <name>motSecTimer</name>
            <id>motSecTimer</id>
            <axis>
                <class></class>
                <name>Timer</name>
                <id>Timer1-mot-double</id>
                <goto>
                    <access method="GETPUTCB" type="double" transport="local">Timer</access>
                </goto>
                <position>
                    <access method="GETCB" type="double" transport="local">Timer</access>
                </position>
                <stop>
                    <access method="PUT" type="int" transport="local">no stop available</access>
                    <value type="int">0</value>
                </stop>
            </axis>
        </motor>
    </motors>
    <devices>
        <device>
            <class></class>
            <name>EVE_SCAN_STATUS</name>
            <id>genPu:fcm:eveStatusmenu</id>
            <value>
                <access method="GETCB" type="string" transport="ca" monitor="true">genPu:fcm:eveStatusmenu</access>
                <value type="string">idle, busy</value>
            </value>
            <option>
                <name>Value</name>
                <id>ValuegenPu:fcm:eveStatusmenu</id>
                <value>
                    <access method="GETCB" type="string" transport="ca" monitor="true">genPu:fcm:eveStatusmenu</access>
                </value>
                <displaygroup>summary</displaygroup>
            </option>
        </device>
    </devices>
</tns:scml>"""


class MockSCML:
    def __init__(self):
        self.root = None
        self.version = ""

    def load(self, xml=SCML_STRING):
        self.root = ET.fromstring(xml)
        self.version = self.root.find("version").text


class MockScan:
    def __init__(self):
        self.version = ""
        self.location = ""
        self.scan = None


class TestVersionMapperFactory(unittest.TestCase):
    def setUp(self):
        self.factory = version_mapping.VersionMapperFactory()
        self.scml = MockSCML()
        self.scml.load()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "scml",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.factory, attribute))

    def test_get_mapper_returns_mapper(self):
        self.factory.scml = self.scml
        mapper = self.factory.get_mapper()
        self.assertIsInstance(mapper, version_mapping.VersionMapper)

    def test_get_mapper_with_scml_argument_sets_scml_property(self):
        self.factory.get_mapper(scml=self.scml)
        self.assertEqual(self.scml, self.factory.scml)

    def test_get_mapper_without_scml_raises(self):
        with self.assertRaises(ValueError):
            self.factory.get_mapper()

    def test_get_mapper_returns_correct_mapper(self):
        self.factory.scml = self.scml
        mapper = self.factory.get_mapper()
        self.assertIsInstance(mapper, version_mapping.VersionMapperV9m2)

    def test_get_mapper_with_unknown_version_raises(self):
        self.scml.version = "0"
        self.factory.scml = self.scml
        with self.assertRaises(AttributeError):
            self.factory.get_mapper()

    def test_get_mapper_sets_source_in_mapper(self):
        self.factory.scml = self.scml
        mapper = self.factory.get_mapper()
        self.assertEqual(self.scml, mapper.source)


class TestVersionMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapper()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "source",
            "destination",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.mapper, attribute))

    def test_map_without_source_raises(self):
        self.mapper.source = None
        with self.assertRaises(ValueError):
            self.mapper.map()

    def test_map_without_destination_raises(self):
        self.mapper.source = MockSCML()
        self.mapper.source.load()
        with self.assertRaises(ValueError):
            self.mapper.map()

    def test_map_sets_basic_metadata(self):
        self.mapper.source = MockSCML()
        self.mapper.source.load()
        destination = MockScan()
        self.mapper.map(destination=destination)
        self.assertEqual(self.mapper.source.version, destination.version)
        self.assertEqual(
            self.mapper.source.root.find("location").text,
            destination.location,
        )


class TestVersionMapperV9m2(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV9m2()

    def test_instantiate_class(self):
        pass

    def test_map_sets_scan_metadata(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            int(self.mapper.source.scan.find("repeatcount").text),
            self.mapper.destination.scan.repeat_count,
        )
        self.assertEqual(
            self.mapper.source.scan.find("comment").text,
            self.mapper.destination.scan.comment,
        )

    def test_map_creates_correct_number_of_scan_modules(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        # Note: Disconnected scan modules have ID>=42 in our example source,
        #       to allow for simpler tests
        connected_scan_modules = [
            module
            for module in self.mapper.source.scan_modules
            if int(module.get("id")) < 42
        ]
        self.assertEqual(
            len(connected_scan_modules),
            len(self.mapper.destination.scan.scan_modules.keys()),
        )

    def test_map_sets_scan_module_attributes(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertEqual(
            self.mapper.source.scan_modules[0].find("name").text,
            self.mapper.destination.scan.scan_modules[15].name,
        )
        self.assertEqual(
            int(self.mapper.source.scan_modules[0].find("parent").text),
            self.mapper.destination.scan.scan_modules[15].parent,
        )
        self.assertEqual(
            int(self.mapper.source.scan_modules[0].find("appended").text),
            self.mapper.destination.scan.scan_modules[15].appended,
        )
        self.assertEqual(
            int(self.mapper.source.scan_modules[1].find("nested").text),
            self.mapper.destination.scan.scan_modules[1].nested,
        )

    def test_map_sets_is_nested_attribute(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(
            self.mapper.destination.scan.scan_modules[2].is_nested
        )

    def test_map_distinguishes_scan_module_types(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        classic_ids = [1, 2]
        snapshot_ids = [15, 3, 4]
        for sm_id in classic_ids:
            self.assertIsInstance(
                self.mapper.destination.scan.scan_modules[sm_id],
                scan.ScanModule,
            )
        for sm_id in snapshot_ids:
            self.assertIsInstance(
                self.mapper.destination.scan.scan_modules[sm_id],
                scan.SnapshotModule,
            )

    def test_map_adds_channels_to_classic_scan_module(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(self.mapper.destination.scan.scan_modules[1].channels)
        for item in self.mapper.destination.scan.scan_modules[
            1
        ].channels.values():
            self.assertIsInstance(item, scan.Channel)
            self.assertTrue(item.id)

    def test_map_adds_axes_to_classic_scan_module(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(self.mapper.destination.scan.scan_modules[1].axes)
        for item in self.mapper.destination.scan.scan_modules[
            1
        ].axes.values():
            self.assertIsInstance(item, scan.Axis)
            self.assertTrue(item.id)

    def test_map_adds_channels_to_static_snapshot_module(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(self.mapper.destination.scan.scan_modules[4].channels)
        for item in self.mapper.destination.scan.scan_modules[
            4
        ].channels.values():
            self.assertIsInstance(item, scan.Channel)
            self.assertTrue(item.id)

    def test_map_adds_axes_to_static_snapshot_module(self):
        self.mapper.source = SCML()
        self.mapper.source.from_string(xml=SCML_STRING)
        destination = Scan()
        self.mapper.map(destination=destination)
        self.assertTrue(self.mapper.destination.scan.scan_modules[3].axes)
        for item in self.mapper.destination.scan.scan_modules[
            3
        ].axes.values():
            self.assertIsInstance(item, scan.Axis)
            self.assertTrue(item.id)
