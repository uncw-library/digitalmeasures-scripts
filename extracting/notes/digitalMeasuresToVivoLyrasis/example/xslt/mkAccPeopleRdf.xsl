<?xml version="1.0"?>
<xsl:stylesheet version='2.0'
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:xs='http://www.w3.org/2001/XMLSchema'
	xmlns:core="http://vivoweb.org/ontology/core#"
	xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:bibo="http://purl.org/ontology/bibo/"
        xmlns:foaf="http://xmlns.com/foaf/0.1/"
        xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
	xmlns:mapid="http://vivoweb.org/ontology/activity-insight"
	xmlns:acti="http://vivoweb.org/ontology/activity-insight#"
	xmlns:dm="http://www.digitalmeasures.com/schema/data"	
	xmlns:vfx='http://vivoweb.org/ext/functions'
	xmlns:hr='http://vivo.cornell.edu/ns/hr/0.9/hr.owl#'
	exclude-result-prefixes='xs vfx dm'
	>

<xsl:output method='xml' indent='yes' normalization-form='NFC'/>
<xsl:strip-space elements="*"/>

<!--

$saxon NewPers.xml xslt/mkAccPeopleRdf.xsl > rdf/NewPers.rdf

-->

<xsl:variable name='NL'>
<xsl:text>
</xsl:text>
</xsl:variable>

<xsl:variable name='localNamespace'>
<xsl:text>http://vivo.cornell.edu/individual/</xsl:text>
</xsl:variable>


<xsl:template match='/ExtantPersons'>
<rdf:RDF>
<xsl:for-each select='person'>

<xsl:if test='vfx:goodName(fname,mname,lname)'>

<rdf:Description rdf:about="{./uri}">
<rdf:type rdf:resource='http://xmlns.com/foaf/0.1/Person'/>


<rdfs:label>
<xsl:value-of select='vfx:mkFullname(fname,mname,lname)'/>
</rdfs:label>

<foaf:firstName>
<xsl:value-of select='normalize-space(fname)'/>
</foaf:firstName>
<!-- designed and coded by Joseph R. Mc Enerney jrm424@cornell.edu -->
<xsl:if test='normalize-space(mname) != ""'>
<core:middleName>
<xsl:value-of select='normalize-space(mname)'/>
</core:middleName>
</xsl:if> 

<foaf:lastName>
<xsl:value-of select='normalize-space(lname)'/>
</foaf:lastName>

<xsl:if test='normalize-space(netid) !=""'>
<hr:netId>
<xsl:value-of select='normalize-space(netid)'/>
</hr:netId>
</xsl:if>

</rdf:Description>

</xsl:if>

</xsl:for-each>
</rdf:RDF>
<xsl:value-of select='$NL'/>
</xsl:template>

<!-- ================================== -->
<xsl:function name='vfx:mkFullname'>
<xsl:param name='fn'/>
<xsl:param name='mn'/>
<xsl:param name='ln'/>
<xsl:variable name='fullname0' select='normalize-space($ln)'/>
<xsl:variable name='fullname1' 
select='if(normalize-space($fn)!="") 
        then 
          concat($fullname0,", ",normalize-space($fn)) 
        else 
        $fullname0'/>
<xsl:variable name='fullname2'
select='if(normalize-space($mn)!="" and $fullname1 = $fullname0)
	then
	  concat($fullname1,", ",normalize-space($mn))
	else
	  concat($fullname1," ",normalize-space($mn))'/>
<xsl:value-of select='normalize-space($fullname2)'/>

</xsl:function>

<xsl:include href='auxfuncs.xsl'/>

</xsl:stylesheet>
