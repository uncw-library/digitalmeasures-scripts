<?xml version="1.0"?>
<xsl:stylesheet version='2.0'
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:vfx='http://vivoweb.org/ext/functions'
	xmlns:xs='http://www.w3.org/2001/XMLSchema'
	exclude-result-prefixes='xs vfx xsl'
>
<!--

Count Distinct UnResolved Org URIs i.e. school URIs 

	$saxon ED0.xml xslt/countUROs.xsl
-->

<xsl:output method='text'/>

<xsl:template match="/EduRecords">

<!-- 
   collect all EduRecords with no school uri. the 'grouping'
   mechanism provides a way to get a list of distinct records
   with the 'same' names
 -->
<xsl:variable name='numgrps' as='node()*'>

<xsl:for-each-group select='EduRecord[edSchoolUri=""]' 
	group-by='vfx:adjust(edSchool)'>
<xsl:copy-of select='.'/>
</xsl:for-each-group>
</xsl:variable>

<!-- output count -->
<xsl:value-of select='concat(count($numgrps),"&#x0A;")'/>

</xsl:template>

<!-- designed and coded by Joseph R. Mc Enerney jrm424@cornell.edu -->

<xsl:include href='auxfuncs.xsl'/>

</xsl:stylesheet>
