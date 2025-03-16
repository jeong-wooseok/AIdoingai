</div><?php // 사이트 콘텐츠 끝 ?>

<footer class="site-footer">
    <div class="container">
        <div class="row">
            <div class="col-md-4">
                <h3 class="widget-title">About Us</h3>
                <p>AI Doing AI는 인공지능 기술과 관련된 최신 정보와 트렌드를 공유하는 블로그입니다.</p>
            </div>
            <div class="col-md-4">
                <h3 class="widget-title">카테고리</h3>
                <?php
                wp_nav_menu(array(
                    'theme_location' => 'footer',
                    'menu_id'        => 'footer-menu',
                    'container'      => false,
                    'fallback_cb'    => false,
                ));
                ?>
            </div>
            <div class="col-md-4">
                <h3 class="widget-title">Contact</h3>
                <p>Email: info@aidoingai.com</p>
                <div class="social-links">
                    <a href="#" target="_blank"><i class="fab fa-twitter"></i></a>
                    <a href="#" target="_blank"><i class="fab fa-facebook"></i></a>
                    <a href="#" target="_blank"><i class="fab fa-instagram"></i></a>
                </div>
            </div>
        </div>
        <div class="site-info">
            <p>&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?>. All Rights Reserved.</p>
        </div>
    </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
<?php wp_footer(); ?>
</body>
</html> 