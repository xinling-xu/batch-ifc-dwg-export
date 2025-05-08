<?xml version="1.0" encoding="utf-8"?>
<Element xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="https://pythonparts.allplan.com/2026/schemas/PythonPart.xsd">
    <Script>
        <Name>allplan_gmbh\DWGExportByFileList.py</Name>
        <Title>DWGExportByFileList</Title>
        <Version>1.0</Version>
        <Interactor>True</Interactor>
        <ReadLastInput>True</ReadLastInput>
    </Script>
    <Page>
        <Name>Drawing</Name>
        <Text>Drawing</Text>
        <Parameters>
            <Parameter>
                <Name>CvsFile</Name>
                <Text>Filename</Text>
                <Value></Value>
                <ValueType>String</ValueType>
                <ValueDialog>OpenFileDialog</ValueDialog>
                <FileFilter>csv-Dateien(*.csv)|*.csv|</FileFilter>
                <FileExtension>csv</FileExtension>
                <DefaultDirectories>etc|std</DefaultDirectories>
            </Parameter>

            <Parameter>
                <Name>StartExportRow</Name>
                <Text> </Text>
                <ValueType>Row</ValueType>
                <Parameters>
                    <Parameter>
                        <Name>StartExportButton</Name>
                        <Text>Export</Text>
                        <EventId>1002</EventId>
                        <ValueType>Button</ValueType>
                    </Parameter>
                </Parameters>
            </Parameter>
        </Parameters>
    </Page>
</Element>