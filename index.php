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
            $cfg_limit_found_words = 100;
            $cfg_limit_found_links_per_words = 100;
        
            // Include some connection info...
            $credentials_file = "C:/CC/xampp-outside-webroot/db_settings.php";    
            include $credentials_file;
            $mysqli = new mysqli('127.0.0.1', $db_user, $db_pass, 'dhbw_crawler');
            
            // Connect to the database...
            if ($mysqli->connect_errno) {
                printf("MySQL connect failed: %s\n", $mysqli->connect_error);
                exit;
            }
            
            // Only if there is a search phrase...
            if ($search != "") {
                // ...perform an SQL query for searching the word in the database. It may be found only once...
                $sql = "SELECT * FROM word WHERE word LIKE '%$search%' LIMIT $cfg_limit_found_words;"; // LIMITED NUMBER OF RESULTS
                if (!$result = $mysqli->query($sql)) {
                    report_problem("Query failed to execute: ". $sql, $mysqli);
                    exit;
                } else {
                    // Open the ul list and loop the word entries...
                    echo "<ul>\n";
                    $record_counter = 0;
                    while ($word_item = $result->fetch_assoc()) {
                        //echo "<li><a href='" . $_SERVER['SCRIPT_NAME'] . "?aid=" . $user['id'] . "'>\n";
                        echo "<li> Result(s) for search phrase [" . $word_item['word'] . "]:\n"; //  (id: " . $word_item['id'] . ")\n";
                        
                        // Finally we query the links being connected to the word entry...
                        $sql="SELECT * FROM wordlinks WHERE id_word = '" . $word_item['id'] . "'  LIMIT $cfg_limit_found_links_per_words;"; // LIMITED NUMBER OF RESULTS
                        if (!$result2 = $mysqli->query($sql)) {
                            report_problem("Query failed to execute: ". $sql, $mysqli);
                            exit;
                        } else {
                            // Open the next level ul list and loop the wordlink entries ...
                            echo "<ul>\n";
                            while ($wordlink_item = $result2->fetch_assoc()) {
                                echo "<li>\n";
                                // Trace: echo "Wordlink found. The id_link is " . $wordlink_item["id_link"] . "</br>\n";
                                
                                // Finally we need the real link...
                                $sql = "SELECT * FROM tbl_link WHERE id = '".$wordlink_item["id_link"]."';";
                                if (!$result3 = $mysqli->query($sql)) {
                                    report_problem("Query failed to execute: ". $sql, $mysqli);
                                    exit;
                                } else {
                                    // We have found the link. So lets display it...
                                    $a_link = $result3->fetch_assoc()['link'];
                                    $record_counter++;
                                    echo "$record_counter - <a href='" . $a_link . "'>" . $a_link . "</a>\n";
                                }
                                echo "</li>\n";
                            }
                            echo "</ul>\n";
                        }
                        // echo $user['firstname'] . ' ' . $user['lastname'];
                        echo "</li>\n";
                    }
                    echo "</ul>\n";

                    // Free the resources...
                    $result->free();
                    $mysqli->close();
                }
            } else {
                echo "Oops, nothing found. => Enter a search phrase!</br>\n";
            }
        ?>
    </body>
</html>