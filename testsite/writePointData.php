<?php
$wind_turbi = $_POST['wind_turbi'];
$xCoord = $_POST['xcoord'];
$yCoord = $_POST['ycoord'];

$dbconn = pg_connect("host=db.qgiscloud.com port=5432 dbname=daqznt_tbcceo user=daqznt_tbcceo password=de3ffb08");

$result = pg_prepare($dbconn, "insertpoint", "INSERT INTO turbine_osk_2022(wind_turbi, geom) VALUES ($1, ST_SetSRID(ST_MakePoint($2, $3),4326))");

$result = pg_execute($dbconn, "insertpoint", array($naam, $xCoord, $yCoord));




// if (pg_affected_rows($result) == 1){
//     $result = pg_prepare($dbconn, "insertdata", "INSERT INTO turbine_osk_2022(wind_turbi, geom) VALUES ($1, ST_SetSRID(ST_MakePoint($2, $3),4326))");

//     $result = pg_execute($dbconn, "insertdata", array($naam, $xCoord, $yCoord));


// }
pg_close($dbconn);

echo pg_affected_rows($result);
?>