<?xml version="1.0"?>
<xsl:stylesheet version='2.0'
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:vfx='http://vivoweb.org/ext/functions'
	xmlns:xs='http://www.w3.org/2001/XMLSchema'
	exclude-result-prefixes='xs vfx xsl'
>
<!--
Count 'name' distinct records with UnResolved Person URIs

	 $saxon ED0.xml xslt/countURPs.xsl
-->
<xsl:output method='text'/>
<xsl:variable name='MYNL'>
<xsl:text>
</xsl:text>
</xsl:variable>
<xsl:template match="/EduRecords">
<!--
 use 'group-by' to collect records with distinct names
-->
<xsl:variable name='cgCounts' as='xs:integer*'>
<xsl:for-each-group select='EduRecord[personUri=""]' 
	group-by='lower-case(concat(normalize-space(ln),"|",
                                    normalize-space(fn),"|",
                                    normalize-space(mn)))'>

<xsl:variable name='gp'>
<xsl:for-each-group select='current-group()' 
				group-by='vfx:adjust(nid)'>
<xsl:copy-of select='.'/>
</xsl:for-each-group>
</xsl:variable>
<xsl:value-of select='count($gp/EduRecord)'/>
</xsl:for-each-group>
</xsl:variable>

<!-- designed and coded by Joseph R. Mc Enerney jrm424@cornell.edu -->

<xsl:value-of select='concat(sum($cgCounts), "&#x0A;")'/>

</xsl:template>


<xsl:include href='auxfuncs.xsl'/>
</xsl:stylesheet>
