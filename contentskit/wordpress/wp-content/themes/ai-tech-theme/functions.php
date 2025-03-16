<?php
/**
 * AI Tech Theme functions and definitions
 */

if (!function_exists('ai_tech_theme_setup')) :
    /**
     * Sets up theme defaults and registers support for various WordPress features.
     */
    function ai_tech_theme_setup() {
        // Add default posts and comments RSS feed links to head.
        add_theme_support('automatic-feed-links');

        // Let WordPress manage the document title.
        add_theme_support('title-tag');

        // Enable support for Post Thumbnails on posts and pages.
        add_theme_support('post-thumbnails');

        // This theme uses wp_nav_menu() in two locations.
        register_nav_menus(array(
            'primary' => esc_html__('Primary Menu', 'ai-tech-theme'),
            'footer'  => esc_html__('Footer Menu', 'ai-tech-theme'),
        ));

        // Switch default core markup to output valid HTML5.
        add_theme_support('html5', array(
            'search-form',
            'comment-form',
            'comment-list',
            'gallery',
            'caption',
        ));

        // Add theme support for Custom Logo.
        add_theme_support('custom-logo', array(
            'height'      => 250,
            'width'       => 250,
            'flex-width'  => true,
            'flex-height' => true,
        ));

        // Add theme support for selective refresh for widgets.
        add_theme_support('customize-selective-refresh-widgets');
    }
endif;
add_action('after_setup_theme', 'ai_tech_theme_setup');

/**
 * Set the content width in pixels, based on the theme's design and stylesheet.
 */
function ai_tech_theme_content_width() {
    $GLOBALS['content_width'] = apply_filters('ai_tech_theme_content_width', 1140);
}
add_action('after_setup_theme', 'ai_tech_theme_content_width', 0);

/**
 * Register widget area.
 */
function ai_tech_theme_widgets_init() {
    register_sidebar(array(
        'name'          => esc_html__('Sidebar', 'ai-tech-theme'),
        'id'            => 'sidebar-1',
        'description'   => esc_html__('Add widgets here.', 'ai-tech-theme'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h2 class="widget-title">',
        'after_title'   => '</h2>',
    ));
}
add_action('widgets_init', 'ai_tech_theme_widgets_init');

/**
 * Enqueue scripts and styles.
 */
function ai_tech_theme_scripts() {
    wp_enqueue_style('ai-tech-theme-style', get_stylesheet_uri(), array(), '1.0.0');
    
    wp_enqueue_script('ai-tech-theme-navigation', get_template_directory_uri() . '/js/navigation.js', array(), '1.0.0', true);

    if (is_singular() && comments_open() && get_option('thread_comments')) {
        wp_enqueue_script('comment-reply');
    }
}
add_action('wp_enqueue_scripts', 'ai_tech_theme_scripts');

/**
 * Custom template tags for this theme.
 */
require get_template_directory() . '/inc/template-tags.php';

/**
 * Functions which enhance the theme by hooking into WordPress.
 */
require get_template_directory() . '/inc/template-functions.php';

/**
 * Customizer additions.
 */
require get_template_directory() . '/inc/customizer.php';

/**
 * Load Jetpack compatibility file.
 */
if (defined('JETPACK__VERSION')) {
    require get_template_directory() . '/inc/jetpack.php';
} 