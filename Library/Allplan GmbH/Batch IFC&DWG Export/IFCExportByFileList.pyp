<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>allplan_gmbh\IFCExportByFileList.py</Name>
        <Title>IFCExportByFileList</Title>
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
                <DefaultDirectories>etc|STD</DefaultDirectories>
            </Parameter>

            <Parameter>
                <Name>StartExportRow</Name>
                <Text> </Text>
                <ValueType>Row</ValueType>

                <Parameter>
                    <Name>StartExportButton</Name>
                    <Text>Export</Text>
                    <EventId>1002</EventId>
                    <ValueType>Button</ValueType>
                </Parameter>
            </Parameter>
        </Parameters>
    </Page>
</Element>