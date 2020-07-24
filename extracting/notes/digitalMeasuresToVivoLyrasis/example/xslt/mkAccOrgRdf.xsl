<?xml version="1.0"?>
<xsl:stylesheet version='2.0'
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:xs='http://www.w3.org/2001/XMLSchema'
	xmlns:core="http://vivoweb.org/ontology/core#"
	xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:bibo="http://purl.org/ontology/bibo/"
        xmlns:foaf="http://xmlns.com/foaf/0.1/"
        xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
	xmlns:acti="http://vivoweb.org/ontology/activity-insight#"
	xmlns:vfx='http://vivoweb.org/ext/functions'
	exclude-result-prefixes='xs vfx'
	>


<xsl:output method='xml' indent='yes' normalization-form='NFC'/>
<xsl:strip-space elements="*"/>
<!--
     $saxon NewOrgs.xml xslt/mkAccOrgRdf.xsl > rdf/NewOrgs.rdf
-->
<xsl:variable name='NL'>
<xsl:text>
</xsl:text>
</xsl:variable>

<xsl:variable name='localNamespace'>
<xsl:text>http://vivo.cornell.edu/individual/</xsl:text>
</xsl:variable>


<xsl:template match='/ExtantOrgs'>
<rdf:RDF>
<!-- designed and coded by Joseph R. Mc Enerney jrm424@cornell.edu -->
<xsl:for-each select='org'>
<xsl:variable name='name' 
	select='normalize-space(name)'/>

<xsl:if test='$name != ""'>

<rdf:Description rdf:about="{./uri}">

<rdf:type rdf:resource='http://xmlns.com/foaf/0.1/Organization'/>

<rdfs:label>
<xsl:value-of select='$name'/>
</rdfs:label>

</rdf:Description>

</xsl:if>

</xsl:for-each>
</rdf:RDF>
<xsl:value-of select='$NL'/>

</xsl:template>


</xsl:stylesheet>
