<?php
    
    error_reporting(0);
   
    if (isset($_GET['search'])) {
        $search = $_GET['search'];
    } else {
        $search = "";
        echo "Search phrase missing...";
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

        <hr>
        <!-- method = get? => argument is visible in URL -->
        <form action="index.php" method="get" style="text-align: center;"> 
            <p>DHBW Search</p>
            <p> <input type="text" name="search" /></p>
            <p><input type="submit" name="search_db" value="Daten absenden"/></p>
        </form>
        <hr>
        
        <h2>Results</h2>
        
        <?php
        
            // Config
            //$cfg_limit_found_words = 100;
            //$cfg_limit_found_links_per_words = 100;
        
            // Include some connection info...
            //$credentials_file = "C:/CC/xampp-outside-webroot/db_settings.php";    
            //include $credentials_file;
            $mysqli = new mysqli("127.0.0.1", "root", "", 'searchengine');
            
           
            
            
            if ($search != "") 
			{
                $sql = "SELECT * FROM word WHERE word LIKE '%$search%' LIMIT 200;"; //Restrict ammount of results from the database
                if ($result = $mysqli->query($sql)) 
				{
                    
					echo "<ul>\n";
					
                    $item_count = 0;
                    while ($word_var = $result->fetch_assoc()) {
                       
					   
                        echo "<li> " . $word_var['word']."  has ID: ". $word_var['id'] . "\n";
                        
                        
                        $sql="SELECT * FROM wordlinks WHERE id_word = '" . $word_var['id'] . "'  LIMIT 200;"; //Restrict ammount of results from the database
						
                        if ($result2 = $mysqli->query($sql)) 
						{
                            
                            echo "<ul>\n";
							
                            while ($wordlink_var = $result2->fetch_assoc()) 
							{	
								
                                echo "<li>\n";
								
                              
                                $sql = "SELECT * FROM links WHERE id = '".$wordlink_var["id_link"]."';";
								
                                if ($result3 = $mysqli->query($sql)) 
								{
                                    
                                    $link_var = $result3->fetch_assoc();
                                    $item_count++;
									//Output of the found site
									echo "$item_count. Wordlink found, the id is: " . $link_var["id"] . " - <a href='" . $link_var["link"] . "'>" . $link_var["link"] . "</a>\n";								
                                    
									
                                }
                                echo "</li>\n";
                            }
                            echo "</ul>\n";
                        }
                        
                        echo "</li>\n";
                    }
                    echo "</ul>\n";

                    // Free the resources...
                    $result->free();
                    $mysqli->close();
                }
            } 
			else 
			{
                echo "Please enter a valid search phrase\n";
            }
        ?>
    </body>
</html>