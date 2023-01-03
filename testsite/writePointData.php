<?php
$datumtijd = $_POST['datumtijd'];
$kroonh = $_POST['kroonh'];
$kroondia = $_POST['kroondia'];
$stamh = $_POST['stamh'];
$bladindex = $_POST['bladindex'];
$xCoord = $_POST['xcoord'];
$yCoord = $_POST['ycoord'];

$dbconn = pg_connect("host=db.qgiscloud.com port=5432 dbname=daqznt_tbcceo user=daqznt_tbcceo password=de3ffb08");

$result = pg_prepare($dbconn, "insertpoint", "INSERT INTO dt_data(datumtijd, kroonh, kroondia, stamh, bladindex, geom) VALUES ($1, $2, $3, $4, $5, ST_SetSRID(ST_MakePoint($6, $7),4326))");

$result = pg_execute($dbconn, "insertpoint", array($datumtijd, $kroonh, $kroondia, $stamh ,$bladindex ,$xCoord, $yCoord));


pg_close($dbconn);

echo pg_affected_rows($result);
?>