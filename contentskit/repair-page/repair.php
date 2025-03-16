<?php
/**
 * 워드프레스 데이터베이스 복구 페이지
 */

// 워드프레스 설정 파일 로드
define('WP_ALLOW_REPAIR', true);
define('ABSPATH', dirname(__FILE__) . '/');

// 워드프레스 설정 파일 경로 찾기
$wp_config_path = dirname(__FILE__) . '/wp-config.php';
if (!file_exists($wp_config_path)) {
    $wp_config_path = dirname(dirname(__FILE__)) . '/wp-config.php';
}

if (file_exists($wp_config_path)) {
    require_once($wp_config_path);
} else {
    die('워드프레스 설정 파일을 찾을 수 없습니다.');
}

// 워드프레스 데이터베이스 클래스 로드
if (file_exists(ABSPATH . 'wp-admin/includes/upgrade.php')) {
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
} else {
    require_once(dirname(ABSPATH) . '/wp-admin/includes/upgrade.php');
}

// 헤더 출력
header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>워드프레스 데이터베이스 복구</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #0073aa;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .button {
            display: inline-block;
            background-color: #0073aa;
            color: #fff;
            padding: 10px 15px;
            text-decoration: none;
            border-radius: 3px;
            margin-right: 10px;
            margin-top: 20px;
        }
        .button:hover {
            background-color: #005177;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-left: 4px solid #0073aa;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>워드프레스 데이터베이스 복구</h1>
        
        <?php
        global $wpdb;
        
        // 데이터베이스 연결 확인
        if (!$wpdb->check_connection()) {
            echo '<div class="result" style="border-left-color: #dc3232;">데이터베이스 연결에 실패했습니다. 설정을 확인해주세요.</div>';
        } else {
            echo '<div class="result">데이터베이스 연결 성공: ' . $wpdb->dbname . '</div>';
            
            // 테이블 목록 가져오기
            $tables = $wpdb->get_results('SHOW TABLES');
            
            if (isset($_GET['repair']) && $_GET['repair'] == 'all') {
                echo '<h2>모든 테이블 복구 결과</h2>';
                echo '<table>';
                echo '<tr><th>테이블</th><th>결과</th></tr>';
                
                foreach ($tables as $table) {
                    $table_name = current($table);
                    $result = $wpdb->get_results("REPAIR TABLE `$table_name`");
                    $status = $result[0]->Msg_text;
                    
                    echo '<tr>';
                    echo '<td>' . $table_name . '</td>';
                    echo '<td>' . $status . '</td>';
                    echo '</tr>';
                }
                
                echo '</table>';
            } else if (isset($_GET['optimize']) && $_GET['optimize'] == 'all') {
                echo '<h2>모든 테이블 최적화 결과</h2>';
                echo '<table>';
                echo '<tr><th>테이블</th><th>결과</th></tr>';
                
                foreach ($tables as $table) {
                    $table_name = current($table);
                    $result = $wpdb->get_results("OPTIMIZE TABLE `$table_name`");
                    $status = $result[0]->Msg_text;
                    
                    echo '<tr>';
                    echo '<td>' . $table_name . '</td>';
                    echo '<td>' . $status . '</td>';
                    echo '</tr>';
                }
                
                echo '</table>';
            } else {
                // 테이블 목록 표시
                echo '<h2>데이터베이스 테이블 목록</h2>';
                echo '<table>';
                echo '<tr><th>테이블 이름</th><th>상태</th></tr>';
                
                foreach ($tables as $table) {
                    $table_name = current($table);
                    $status = $wpdb->get_var("CHECK TABLE `$table_name` QUICK");
                    
                    echo '<tr>';
                    echo '<td>' . $table_name . '</td>';
                    echo '<td>' . ($status ? $status : 'OK') . '</td>';
                    echo '</tr>';
                }
                
                echo '</table>';
                
                echo '<a href="?repair=all" class="button">모든 테이블 복구</a>';
                echo '<a href="?optimize=all" class="button">모든 테이블 최적화</a>';
            }
        }
        ?>
    </div>
</body>
</html> 