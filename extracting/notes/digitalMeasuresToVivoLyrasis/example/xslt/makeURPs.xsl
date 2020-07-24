<?xml version="1.0"?>
<xsl:stylesheet version='2.0'
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:vfx='http://vivoweb.org/ext/functions'
	xmlns:xs='http://www.w3.org/2001/XMLSchema'
	exclude-result-prefixes='xs vfx xsl'
>

<xsl:param name='unoMapFile'  required='yes'/>

<xsl:output method='xml' indent='yes' normalization-form='NFC'/>

<xsl:variable name='localNamespace'>
<xsl:text>http://vivo.cornell.edu/individual/</xsl:text>
</xsl:variable>

<xsl:variable name='MYNL'><xsl:text>
</xsl:text></xsl:variable>

<xsl:variable name='unomap'
	select="document($unoMapFile)/Mapping"/>

<xsl:template match="/EduRecords">
<ExtantPersons>
<xsl:text>   </xsl:text>

<xsl:variable name='cgCounts' as='xs:integer*'>
<xsl:for-each-group select='EduRecord[personUri=""]' 
	group-by='lower-case(concat(normalize-space(ln),"|",
                                    normalize-space(fn),"|",
                                    normalize-space(mn)))'>

<xsl:variable name='cg' select='current-group()' />

<xsl:variable name='gp'>
<xsl:for-each-group select='$cg' group-by='vfx:adjust(nid)'>
<xsl:copy-of select='.'/>
</xsl:for-each-group>
</xsl:variable>

<xsl:value-of select='count($gp/EduRecord)'/>
</xsl:for-each-group>
</xsl:variable>

<xsl:variable name='cumulativeCgCounts' as='xs:integer*'>
<xsl:call-template name='cumulativeSum'>
<xsl:with-param name='vals' select='$cgCounts'/>
<xsl:with-param name='seq' select='()'/>
</xsl:call-template>
</xsl:variable>

<xsl:for-each-group select='EduRecord[personUri=""]' 
	group-by='lower-case(concat(normalize-space(ln),"|",
                                    normalize-space(fn),"|",
                                    normalize-space(mn)))'>

<xsl:variable name='posA' select='position()'/>
<xsl:variable name='cg' select='current-group()'/>

<xsl:for-each-group select='$cg' group-by='vfx:adjust(nid)'>

<xsl:variable name='posB' select='position()'/>
<xsl:variable name='index' 
	select='$posB + xs:integer($cumulativeCgCounts[$posA])'/>

<xsl:variable name='u' 
   	select='$unomap/map[@n = $index]/@nuno'/>

<xsl:call-template name='makePerson'>
<xsl:with-param name='fn' select='fn'/>
<xsl:with-param name='mn' select='mn'/>
<xsl:with-param name='ln' select='ln'/>
<xsl:with-param name='uri' 
	select='concat($localNamespace,$u)'/>
<xsl:with-param name='nid' select='./nid'/>
</xsl:call-template>

</xsl:for-each-group>

</xsl:for-each-group>

</ExtantPersons>
<xsl:value-of select='$MYNL'/>

</xsl:template>

<xsl:template name='makePerson'>
<xsl:param name='fn'/>
<xsl:param name='mn'/>
<xsl:param name='ln'/>
<xsl:param name='uri'/>
<xsl:param name='nid'/>
<person>
<fname><xsl:value-of select='$fn'/></fname>
<mname><xsl:value-of select='$mn'/></mname>
<lname><xsl:value-of select='$ln'/></lname>
<uri><xsl:value-of select='$uri'/></uri>
<netid><xsl:value-of select='$nid'/></netid>
</person>
</xsl:template>

<xsl:template name='cumulativeSum'>

<xsl:param name='vals'/>

<xsl:param name='seq' />

<xsl:param name='nxtval' select='0'/>

<xsl:choose>
<xsl:when test='not(empty($vals))'>

<xsl:call-template name='cumulativeSum'>

<xsl:with-param name='vals' select='$vals[position()>1]'/>

<xsl:with-param name='seq' select='($seq,$nxtval)'/>

<xsl:with-param name='nxtval' select='$nxtval+$vals[1]'/>

</xsl:call-template>

</xsl:when>
<xsl:otherwise>

<xsl:sequence select='$seq'/>

</xsl:otherwise>
</xsl:choose>

</xsl:template>


<xsl:include href='auxfuncs.xsl'/>
</xsl:stylesheet>
