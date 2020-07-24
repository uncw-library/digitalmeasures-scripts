<?xml version="1.0"?>
<xsl:stylesheet version='2.0'
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:vfx='http://vivoweb.org/ext/functions'
	xmlns:xs='http://www.w3.org/2001/XMLSchema'
	exclude-result-prefixes='xs vfx xsl'
>

<!--
To gather all 'good' rows from the EDU Result Set execute the following call
 from xslt parent directory:

 $saxon EduRS.xml xslt/gather.xsl extPerIn=`pwd`/acc/Per0.xml extOrgIn=`pwd`/acc/Org0.xml > ED0.xml
-->

<xsl:param name='extOrgIn' required='yes'/>
<xsl:param name='extPerIn' required='yes'/>

<xsl:output method='xml' indent='yes' normalization-form='NFC'/>
<xsl:strip-space elements="*"/>

<xsl:variable name='localNamespace'>
<xsl:text>http://vivo.cornell.edu/individual/</xsl:text>
</xsl:variable>

<xsl:variable name='MYNL'>
<xsl:text>
</xsl:text>
</xsl:variable>

<xsl:variable name='extantPersons'
	select="document($extPerIn)/ExtantPersons"/>

<xsl:variable name='extantOrgs'
	select="document($extOrgIn)/ExtantOrgs"/>



<xsl:template match='/ROWS'>
<EduRecords>
<xsl:for-each select='ROW'>

<xsl:if test='DEGREE != "" and MAJOR != "" and YEAR != "" and
              FNAME != "" and LNAME != "" and INSTITUTION != ""'>
<EduRecord>
<xsl:variable name='thisId' select='@id'/>
<xsl:variable name='school' select='normalize-space(INSTITUTION)'/>

<xsl:variable name='schoolUri' 
    select='$extantOrgs/org[vfx:adjust(name) = upper-case($school)]/uri'/>

<edId><xsl:value-of select='$thisId'/></edId>
<edUri><xsl:value-of 
    select='concat($localNamespace,"EX-",$thisId)'/></edUri>
<edDeg><xsl:value-of select='normalize-space(DEGREE)'/></edDeg>
<edMajor><xsl:value-of select='normalize-space(MAJOR)'/></edMajor>
<edYear><xsl:value-of select='normalize-space(YEAR)'/></edYear>

<edSchoolUri>
<xsl:value-of 
	select='if(count($schoolUri)>0)then $schoolUri[1] else ""'/>
</edSchoolUri>

<edSchool><xsl:value-of select='$school'/></edSchool>
<fn><xsl:value-of select='normalize-space(./FNAME)'/></fn>
<mn><xsl:value-of select='normalize-space(./MNAME)'/></mn>
<ln><xsl:value-of select='normalize-space(./LNAME)'/></ln>
<nid><xsl:value-of select='normalize-space(NETID)'/></nid>

<!-- look for matching foaf:Person uri -->
<xsl:variable name='kuri' 
	select='vfx:findMatchingPeople(FNAME, MNAME, LNAME, NETID, 
                                         $extantPersons)'/>
<personUri><xsl:value-of select='$kuri'/></personUri>

</EduRecord>
</xsl:if>
</xsl:for-each>
</EduRecords><xsl:value-of select='$MYNL'/>
</xsl:template>
<!-- designed and coded by Joseph R. Mc Enerney jrm424@cornell.edu -->
<xsl:include href='auxfuncs.xsl'/>
</xsl:stylesheet>
