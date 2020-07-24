<?xml version="1.0"?>
<xsl:stylesheet version='2.0'
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:vfx='http://vivoweb.org/ext/functions'
	xmlns:xs='http://www.w3.org/2001/XMLSchema'
	exclude-result-prefixes='xs vfx xsl'
>
<!-- 
  $saxon ED0.xml xslt/makeUROs.xsl unoMapFile=`pwd`/EX-URO-UNOs.xml > NewOrgs.xml
-->
<xsl:param name='unoMapFile'  required='yes'/>
<xsl:output method='xml' indent='yes' normalization-form='NFC'/>

<xsl:variable name='localNamespace'>
<xsl:text>http://vivo.cornell.edu/individual/</xsl:text>
</xsl:variable>

<xsl:variable name='MYNL'>
<xsl:text>
</xsl:text>
</xsl:variable>
<xsl:variable name='unomap'
	select="document($unoMapFile)/Mapping"/>

<xsl:template match="/EduRecords">
<ExtantOrgs>
<xsl:comment><xsl:value-of select='count($unomap/map)'/></xsl:comment><xsl:text>
   </xsl:text>
<xsl:for-each-group select='EduRecord[edSchoolUri=""]' 
	group-by='lower-case(normalize-space(edSchool))'>
<xsl:variable name='pos' select='position()'/>
<xsl:variable name='u' select='$unomap/map[@n = $pos]/@nuno'/>
<org>
<!-- designed and coded by Joseph R. Mc Enerney jrm424@cornell.edu -->
<uri>
<xsl:value-of select='concat($localNamespace,$u)'/>
</uri>
<name><xsl:value-of select='normalize-space(edSchool)'/></name>

</org>
<xsl:value-of select='$MYNL'/>
</xsl:for-each-group>

</ExtantOrgs>
<xsl:value-of select='$MYNL'/>

</xsl:template>


</xsl:stylesheet>
