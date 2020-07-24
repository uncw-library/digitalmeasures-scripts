<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:dm="http://www.digitalmeasures.com/schema/data"
xmlns:dmd="http://www.digitalmeasures.com/schema/data-metadata"
xmlns:ai="http://www.digitalmeasures.com/schema/data"
xmlns:xs='http://www.w3.org/2001/XMLSchema'
xmlns:vfx='http://vivoweb.org/ext/functions'	
xmlns:core="http://vivoweb.org/ontology/core#"
xmlns:acti="http://vivoweb.org/ontology/activity-insight#"
xmlns:bibo="http://purl.org/ontology/bibo/"
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
exclude-result-prefixes='vfx xs dm dmd ai'
 version="2.0">   

<xsl:function name='vfx:findMatchingPeople'>
<xsl:param name='fn'/>
<xsl:param name='mn'/>
<xsl:param name='ln'/>
<xsl:param name='nid'/>
<xsl:param name='ep'/>

<xsl:variable name='nidMatches' 
   select='$ep/person[vfx:adjust(netid) = vfx:adjust($nid) and
                      vfx:adjust($nid) != ""]/uri'/>

<xsl:variable name='npMatches' 
  select='$ep/person[vfx:namesMatch(fname,mname,lname,
                                    $fn,$mn,$ln) and string(netid) = ""]/uri'/>

<xsl:variable name='results' as='node()*'
   select='if(vfx:adjust($nid) = "")
           then $npMatches
           else $nidMatches'/>

<xsl:value-of select='string($results[1])'/>
</xsl:function>

<xsl:function name='vfx:findMatchingPeopleII'>
<xsl:param name='fn'/>
<xsl:param name='mn'/>
<xsl:param name='ln'/>
<xsl:param name='nid'/>
<xsl:param name='ep'/>
<xsl:variable name='results' 
	select='$ep/person[vfx:adjust(lname) = vfx:adjust($ln) and
                           vfx:adjust(fname) = vfx:adjust($fn) and
                           vfx:adjust(mname) = vfx:adjust($mn) and
		           vfx:adjust(netid) = vfx:adjust($nid)]/uri'/>
<xsl:value-of select='$results[1]'/>
</xsl:function>



<xsl:function name='vfx:findMatchingPeopleIII'>
<xsl:param name='fn'/>
<xsl:param name='mn'/>
<xsl:param name='ln'/>
<xsl:param name='nid'/>
<xsl:param name='ep'/>

<xsl:variable name='nidMatches' 
	select='$ep/person[vfx:adjust(netid) = vfx:adjust($nid)]/uri'/>

<xsl:variable name='results' as='node()*'
   select='if(vfx:adjust($nid) = "")
           then $ep/person[vfx:namesMatch(fname,mname,lname,
                                          $fn,$mn,$ln) and netid = ""]/uri
           else if(count($nidMatches)>0)
                then $nidMatches
                else $ep/person[vfx:namesMatch(fname,mname,lname,
                                               $fn,$mn,$ln)]/uri'/>
<xsl:value-of select='$results[1]'/>
</xsl:function>



<xsl:function name='vfx:findMatchingPeopleIV'>
<xsl:param name='fn'/>
<xsl:param name='mn'/>
<xsl:param name='ln'/>
<xsl:param name='nid'/>
<xsl:param name='ep'/>

<xsl:variable name='nidMatches' 
	select='$ep/person[vfx:adjust(netid) = vfx:adjust($nid)]/uri'/>

<xsl:variable name='npMatches' 
	select='$ep/person[vfx:namesMatchMNIO(fname,mname,lname,
                                              $fn,$mn,$ln)]/uri'/>
<xsl:variable name='results'  as='node()*'
	select='if(vfx:adjust($nid) = "")
                then $npMatches
                else if(count($nidMatches)>0)
                     then 
		        $nidMatches
                     else 
		        $npMatches'/>

<xsl:value-of select='$results[1]'/>
</xsl:function>


<xsl:function name='vfx:adjust'>
<xsl:param name='s'/>
<xsl:value-of select='upper-case(normalize-space(string($s)))'/>
</xsl:function>

<xsl:function name='vfx:initial'>
<xsl:param name='s'/>
<xsl:value-of select='substring(normalize-space(string($s)),1,1)'/>
</xsl:function>

<xsl:function name='vfx:namesMatch' as='xs:boolean'>
<xsl:param name='f1'/>
<xsl:param name='m1'/>
<xsl:param name='l1'/>
<xsl:param name='f2'/>
<xsl:param name='m2'/>
<xsl:param name='l2'/>
<xsl:value-of select='vfx:adjust($l1) = vfx:adjust($l2) and
		      vfx:adjust($f1) = vfx:adjust($f2) and
 		      vfx:adjust($m1) = vfx:adjust($m2)'/>
</xsl:function>

<!-- Middle Name 'Initial Only' type of match -->
<xsl:function name='vfx:namesMatchMNIO' as='xs:boolean'>
<xsl:param name='f1'/>
<xsl:param name='m1'/>
<xsl:param name='l1'/>
<xsl:param name='f2'/>
<xsl:param name='m2'/>
<xsl:param name='l2'/>
<xsl:value-of select='vfx:adjust($l1) = vfx:adjust($l2) and
		      vfx:adjust($f1) = vfx:adjust($f2) and
 		      vfx:initial(vfx:adjust($m1)) = 
                            vfx:initial(vfx:adjust($m2))'/>
</xsl:function>


<xsl:template name='addDtiYear'>
<xsl:param name='uri'/>
<xsl:param name='year'/>
<xsl:if test='$year != ""'>
<core:dateTimeInterval>
<rdf:Description rdf:about="{$uri}">
<rdf:type 
   rdf:resource="http://vivoweb.org/ontology/core#DateTimeInterval"/>

<core:end>
  <rdf:Description rdf:about="{concat($uri,'-E')}">
     <rdf:type 
	rdf:resource="http://vivoweb.org/ontology/core#DateTimeValue"/>
     <core:dateTime 
	rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">
	  <xsl:value-of select='concat(format-number(number($year),"0000"),
                                       "-01-01T00:00:00")'/>
     </core:dateTime>
     <core:dateTimePrecision 
         rdf:resource="http://vivoweb.org/ontology/core#yearPrecision"/>
    </rdf:Description>
</core:end>

</rdf:Description>
</core:dateTimeInterval>
</xsl:if>
</xsl:template>

<xsl:function name='vfx:goodName' as='xs:boolean'>
<xsl:param name='fn'/>
<xsl:param name='mn'/>
<xsl:param name='ln'/>
<xsl:value-of select='if(string($fn) = "" or string($ln) = "") 
                      then false() 
                      else true()'/>
</xsl:function>

<xsl:function name='vfx:capitalize-name-part'>
<xsl:param name='p'/>
<xsl:value-of select='concat(upper-case(substring($p,1,1)),
                             lower-case(substring($p,2)))'/>
</xsl:function>

<xsl:function name='vfx:capitalize-first'>
<xsl:param name='p'/>
<xsl:value-of select='concat(upper-case(substring($p,1,1)),
                             substring($p,2))'/>
</xsl:function>


</xsl:stylesheet>
