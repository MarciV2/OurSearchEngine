<?php

    //Supress Warnings/errors If you can not see them they do not exist
    error_reporting(0);
   
    if (isset($_GET['search'])) {
        $search = $_GET['search'];
    } else {
        $search = "";
        
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
			 <p><input type="submit" value="Link hinzufügen"</p>
        </form>

        <hr>
        
        <form action="index.php" method="get" style="text-align: center;"> 
            <p>DHBW Search</p>
            <p> <input type="text" name="search" /></p>
            <p><input type="submit" name="search_db" value="Daten absenden"/></p>
        </form>
        <hr>
        
        <h2>Results</h2>
        
        <?php
        
           
            
            
           
            if ($search != "") 
			{
				$mysqli = new mysqli("127.0.0.1", "root", "", 'searchengine');
				//Count the total ammount of links safed
				$sql = "SELECT COUNT(*) as total from links;";
				if ($result = $mysqli->query($sql)) 
				{
					$count_links = $result->fetch_assoc();
					
					if($count_links['total']!=0)
						echo"There are currently <b>" .$count_links['total']. " </b>links safed in total!";
					else echo"There are currently no links safed";
					echo"<br>";
					
					//Count the ammount of words safed in total
					$sql = "SELECT COUNT(*) as total from words;";
					if ($result = $mysqli->query($sql)) 
					{
						$count_words = $result->fetch_assoc();
					
						if($count_words['total']!=0)
						{
							echo"There are currently <b>" .$count_words['total']. "</b> words safed in total!";
							echo"<br>";
							
							//Search for the word with the most uses
							$sql = "SELECT COUNT(id_link)as total , id_word from wordlinks GROUP BY id_word ORDER BY total DESC;";
							if ($result = $mysqli->query($sql)) 
							{
								$count_uses = $result->fetch_assoc();
								$sql = "SELECT id, word from words WHERE id='" . $count_uses['id_word'] . "';";
								if ($result = $mysqli->query($sql)) 
								{
									$most_used_word = $result->fetch_assoc();
									echo"The most used word is <b>" . $most_used_word['word']."</b> with an id of <b>" . $most_used_word['id']. ",</b> it is  used a total of <b>".$count_uses['total']."</b> times!";
						
								}
							}
						}
						else echo"There are currently no words safed";
					}	
				}
				
                $sql = "SELECT * FROM words WHERE word LIKE '%$search%' LIMIT 200;"; //Restrict ammount of results from the database
                if ($result = $mysqli->query($sql)) 
				{
                    
					echo "<ul>\n";
					
                    $item_count = 0;
                    while ($word_var = $result->fetch_assoc()) {
                       
						//Found word with id within the loop 
                        echo "<li> <b>" . $word_var['word']."</b>  has ID: <b>". $word_var['id'] . "</b>\n";
                        
                        //Wordlink for the given id
                        $sql="SELECT * FROM wordlinks WHERE id_word = '" . $word_var['id'] . "'  LIMIT 200;"; //Restrict ammount of results from the database
						
                        if ($result2 = $mysqli->query($sql)) 
						{
                            
                            echo "<ul>\n";
							
                            while ($wordlink_var = $result2->fetch_assoc()) 
							{	
								
                                echo "<li>\n";
								
								//Get the link from the found id_link
                                $sql = "SELECT * FROM links WHERE id = '".$wordlink_var["id_link"]."';";
								
                                if ($result3 = $mysqli->query($sql)) 
								{
                                    
                                    $link_var = $result3->fetch_assoc();
                                    $item_count++;
									
									//Output of the Link and its id
									echo "<b>$item_count.</b> Wordlink with the title: <b>" . $link_var["title"] . "</b> found, the id is: <b>" . $link_var["id"] . "</b> - <a href='" . $link_var["link"] . "'>" . $link_var["link"] . "</a>\n";								
                                    
									
                                }
                                echo "</li>\n";
                            }
                            echo "</ul>\n";
							
                        }
                        
                        echo "</li>\n";
                    }
                    echo "</ul>\n";

                    
                    $result->free();
					$result2->free();
					$result3->free();
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