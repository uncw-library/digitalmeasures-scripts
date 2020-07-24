<?xml version="1.0"?>
<xsl:stylesheet version='2.0'
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:vfx='http://vivoweb.org/ext/functions'
	xmlns:xs='http://www.w3.org/2001/XMLSchema'
	xmlns:dm="http://www.digitalmeasures.com/schema/data"
	xmlns:mapid="http://vivoweb.org/ontology/activity-insight"
	xmlns:core="http://vivoweb.org/ontology/core#"
	xmlns:vivo="http://vivoweb.org/ontology/core#"
	xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:bibo="http://purl.org/ontology/bibo/"
        xmlns:foaf="http://xmlns.com/foaf/0.1/"
        xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
	xmlns:acti="http://vivoweb.org/ontology/activity-insight#"
        xmlns:local="http://vivo.cornell.edu/ontology/local#"
	exclude-result-prefixes='xs vfx xsl dm mapid'
>


<!--
	$saxon ED2.xml xslt/mkEduRdf.xsl > rdf/ED.rdf
-->
<xsl:output method='xml' indent='yes' normalization-form='NFC'/>
<xsl:variable name='NL'>
<xsl:text>
</xsl:text>
</xsl:variable>

<xsl:variable name='localNamespace'>
<xsl:text>http://vivo.cornell.edu/individual/</xsl:text>
</xsl:variable>


<xsl:template match='/EduRecords'>
<rdf:RDF>
<xsl:value-of select='concat($NL,"   ")'/>
<xsl:for-each select='./EduRecord'>
<xsl:value-of select='concat($NL,"   ")'/>
<xsl:comment>
<xsl:value-of select='concat("EduRec ",position())'/>
</xsl:comment>
<xsl:value-of select='concat($NL,"   ")'/>

<rdf:Description rdf:about="{edUri}" >
<rdf:type rdf:resource=
	'http://vivoweb.org/ontology/core#EducationalTraining'/>

<local:degreeLevel>
	<xsl:value-of select='normalize-space(edDeg)'/>
</local:degreeLevel>

<xsl:if test='not(nid) or nid = ""'>
	<local:weakAttribution>
	<xsl:value-of select='"true"'/>
	</local:weakAttribution>
</xsl:if>

<rdfs:label>
<xsl:value-of select='normalize-space(concat(edDeg,", ",edMajor))'/>
</rdfs:label>

<core:majorField>
<xsl:value-of select='edMajor'/>
</core:majorField>

<xsl:call-template name='addDtiYear'>
<xsl:with-param name='uri' select='concat(edUri,"-DTV")'/>
<xsl:with-param name='year' select='edYear'/>
</xsl:call-template>

<core:trainingAtOrganization>
<xsl:comment>
<xsl:value-of select='edSchool'/>
</xsl:comment><xsl:text>
</xsl:text>
<xsl:value-of select='"         "'/>
<rdf:Description rdf:about="{edSchoolUri}">
</rdf:Description>
</core:trainingAtOrganization>

<!-- designed and coded by Joseph R. Mc Enerney jrm424@cornell.edu -->

<core:educationalTrainingOf>
<xsl:comment>
<xsl:value-of select='concat(ln,", ",fn," ",mn," (",nid,")")'/>
</xsl:comment><xsl:text>
</xsl:text>
<xsl:value-of select='"         "'/>
<rdf:Description rdf:about="{personUri}">
<core:educationalTraining rdf:resource="{edUri}" />
</rdf:Description>
</core:educationalTrainingOf>

</rdf:Description>
</xsl:for-each>
</rdf:RDF>
<xsl:text>
</xsl:text>
</xsl:template>

<xsl:include href='auxfuncs.xsl'/>

</xsl:stylesheet>
