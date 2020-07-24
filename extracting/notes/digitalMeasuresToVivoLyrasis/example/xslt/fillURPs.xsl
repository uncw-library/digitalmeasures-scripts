<?xml version="1.0"?>
<xsl:stylesheet version='2.0'
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:vfx='http://vivoweb.org/ext/functions'
	xmlns:xs='http://www.w3.org/2001/XMLSchema'
	exclude-result-prefixes='xs vfx xsl'
>

<xsl:param name='extPerIn' required='yes'/>

<xsl:output method='xml' indent='yes' normalization-form='NFC'/>
<xsl:strip-space elements="*"/>

<xsl:variable name='localNamespace'>
<xsl:text>http://vivo.cornell.edu/individual/</xsl:text>
</xsl:variable>


<xsl:variable name='extantPersons'
	select="document($extPerIn)/ExtantPersons"/>
<!--
Resolve UnResolved Persons

	$saxon ED1.xml xslt/fillURPs.xsl extPerIn=`pwd`/NewPers.xml > ED2.xml
-->

<xsl:template match="/EduRecords">
<EduRecords>
<xsl:for-each select='EduRecord'>
<xsl:copy>
<xsl:for-each select='*'>

<xsl:choose>
<xsl:when test='name() = "personUri" and . = ""'>
<xsl:variable name='nid' select='../nid'/>
<xsl:variable name='f' select='../fn'/>
<xsl:variable name='m' select='../mn'/>
<xsl:variable name='l' select='../ln'/>
<xsl:variable name='kuri' 
	select='vfx:findMatchingPeopleII($f, $m, $l, $nid, $extantPersons)'/>
<personUri><xsl:value-of select='$kuri[1]'/></personUri>
</xsl:when>
<xsl:otherwise>
<xsl:copy-of select='.'/>
</xsl:otherwise>
</xsl:choose>
</xsl:for-each>
</xsl:copy>
</xsl:for-each>
</EduRecords>
<xsl:text>
</xsl:text>
</xsl:template>
<!-- designed and coded by Joseph R. Mc Enerney jrm424@cornell.edu -->

<xsl:include href='auxfuncs.xsl'/>

</xsl:stylesheet>
