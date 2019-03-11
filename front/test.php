<?php 
header('Content-Type:text/json;charset=utf-8');
ini_set("display_errors", "On");
//error_reporting(E_ALL | E_STRICT);
error_reporting(1);
ini_set('memory_limit', '1024M');
set_time_limit(0);
//ignore_user_abort(); // 后台运行  

require_once 'vendor/autoload.php';
use Fukuball\Jieba\Jieba;
use Fukuball\Jieba\Finalseg;

function find($str){
	global $mysqli;
	$mysqli->set_charset("utf8");
	
	if ($mysqli->connect_errno) 
	{ 
	    echo "连接 MySQL 失败: " . mysqli_connect_error(); 
	}
	$sql = "select * from invert_index where words='".$str."'";

	$result=$mysqli->query($sql);

	$num_results = $result -> num_rows; //结果行数
	//echo $num_results;
	//echo "<br>";

	if(!$result){
		//echo json_encode("");
		echo "sql语句错误<br/>";
		echo "error:".$mysqli->error."|".$mysqli->error;
	}

	global $result_array;
	for($i = 0;$i < $num_results;$i++)//循环输出每组元素
	{
		$row = $result -> fetch_assoc();//提取元素，一次一行，fetch_assoc()提取出的元素，有属性以及值
		$url = stripcslashes(($row['url']));
		$tf_idf = stripcslashes($row['tf_idf']);
		//echo $url." ".$tf_idf."   ";
		if(array_key_exists($url,$result_array)){
			$result_array[$url]+=$tf_idf;
		}
		else{
			$result_array[$url] = 0+$tf_idf;
		}
	}
}

 
	
function search($url)
{
	global $return_array;
	global $mysqli;
	$mysqli->set_charset("utf8");
	if ($mysqli->connect_errno) 
	{ 
	    echo "连接 MySQL 失败: " . mysqli_connect_error(); 
	}

	$sql = "select * from `properties` where url='".$url."'";
	$result=$mysqli->query($sql);
	if(!$result){
		//echo json_encode("");
		echo "sql语句错误<br/>";
		echo "error:".$mysqli->error."|".$mysqli->error;
	}
	$row = $result -> fetch_assoc();//提取元素，一次一行，fetch_assoc()提取出的元素，有属性以及值
	$url = stripcslashes(($row['url']));
	$title = stripcslashes($row['title']);
	$description = stripcslashes($row['description']);
	$keywords = stripcslashes($row['keywords']);
	$return_array[]=array("url"=>$url,"title"=>$title,"description"=>$description,"keywords"=>$keywords,);

}


session_start();
//echo $_POST['question'];
//echo "<br>";
if($_POST['question']!='')
{
	Jieba::init();
	Finalseg::init();

	$mysqli = new mysqli("127.0.0.1", "root", "mimamima", "news");
	$result_array=[];
	$return_array=[];
	$seg_list=Jieba::cutForSearch($_POST['question']);

	//var_dump($seg_list);
	//echo "<br>";

	if(count($seg_list)==0){
		echo json_encode("");
		exit();
	}

	foreach ($seg_list as $value){
		//print($value." ");
		find($value);
	}
	if(count($result_array)==0){
		echo json_encode("");
		exit();
	}
	arsort($result_array);
	foreach ($result_array as $key=>$value){
		search($key);
	}
	if(count($return_array)==0){
		echo json_encode("");
		exit();
	}
	echo json_encode($return_array , JSON_UNESCAPED_UNICODE), "\n";

	$mysqli->close();
}
else
{
	echo("don't enter any words");
	exit();
}

?> 
