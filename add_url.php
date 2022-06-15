<?php

	//Supress Warnings/errors If you can not see them they do not exist
	error_reporting(0);
	if (isset($_GET['url'])) {
        $url = $_GET['url'];
    } else {
        $url = "";
        echo "'url' argument phrase missing...";
    }

		
	
	 
		
		 
	if($url=="")
	{
		echo("Url is empty");	
	}
	else
	{
		
	$mysqli = new mysqli("127.0.0.1", "root", "", 'searchengine');
		
		
	
	$sql = "SELECT * from links WHERE link = '$url';";
	
	//Already in Database?
	if ($result_r = $mysqli->query($sql)) 
	{
				
		if ($result_r->num_rows > 0) 
		{
			
			echo("Link is already in database");
			
		}
		else
		{
		// Insert new link
		$sql = "INSERT INTO links (link, timestamp_visited) VALUES ('$url','0000-00-00 00:00:00');";
		echo $sql . "<br>";
			if ($result = $mysqli->query($sql)) 
			{
				echo("Link inserted into database");
						
			} 
			else 
			{
				echo("Database error");
			}            
		}
		$result_r->close();
	}   
		  
	$mysqli->close(); 
	}
?>
<!DOCTYPE html>
<html lang="de">
    <head>
        
        <meta charset="utf-8">
        <title>Searchengine</title>
    </head>

    <body>
        
        <form action="add_url.php" method="get"> 
             <p>DHBW Add URL to Database: <input type="text" name="url" /></p>
             <p> (<b>HINT:</b> USE 'http' or 'https' like, <b>http://www.xyz.de</b>)</p>
			 <p><input type="submit" value="Link hinzufügen"</p>
        </form>
		<form action="index.php" method="post"> 
			 <p><input type="submit" value="Zurück auf Hauptseite"</p>
        </form>

       
    </body>
</html>