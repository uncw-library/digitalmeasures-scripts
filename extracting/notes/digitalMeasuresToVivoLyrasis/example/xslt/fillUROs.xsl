<?xml version="1.0"?>
<xsl:stylesheet version='2.0'
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:vfx='http://vivoweb.org/ext/functions'
	xmlns:xs='http://www.w3.org/2001/XMLSchema'
	exclude-result-prefixes='xs vfx xsl'
>
<!--
Use new Orgs to resolve UnResolved Orgs 

	$saxon ED0.xml xslt/fillUROs.xsl extOrgIn=`pwd`/NewOrgs.xml > ED1.xml
-->
<xsl:param name='extOrgIn' required='yes'/>
<xsl:output method='xml' indent='yes' normalization-form='NFC'/>
<xsl:strip-space elements="*"/>

<xsl:variable name='localNamespace'>
<xsl:text>http://vivo.cornell.edu/individual/</xsl:text>
</xsl:variable>

<xsl:variable name='extantOrgs'
	select="document($extOrgIn)/ExtantOrgs"/>
<!--
$SAXON ED0.xml `aiw x`/newED/fillUROs.xsl extOrgIn=`pwd`/NewEdOrgs.xml  > ED1.xml
-->

<xsl:template match="/EduRecords">
<EduRecords>
<xsl:for-each select='EduRecord'>
<xsl:copy>
<xsl:for-each select='*'>
<xsl:choose>
<xsl:when test='name() = "edSchoolUri" and . = ""'>

<xsl:variable name='edSchool' select='lower-case(normalize-space(../edSchool))'/>
<!-- designed and coded by Joseph R. Mc Enerney jrm424@cornell.edu -->
<xsl:variable name='kuri' 
	select='$extantOrgs/org[lower-case(normalize-space(name)) = $edSchool]/uri'/>
<edSchoolUri><xsl:value-of select='$kuri[1]'/></edSchoolUri>
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

</xsl:stylesheet>
