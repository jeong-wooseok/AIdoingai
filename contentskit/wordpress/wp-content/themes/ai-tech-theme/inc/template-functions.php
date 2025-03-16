<?php
/**
 * Functions which enhance the theme by hooking into WordPress
 */

/**
 * Adds custom classes to the array of body classes.
 *
 * @param array $classes Classes for the body element.
 * @return array
 */
function ai_tech_theme_body_classes($classes) {
    // Adds a class of hfeed to non-singular pages.
    if (!is_singular()) {
        $classes[] = 'hfeed';
    }

    // Adds a class of no-sidebar when there is no sidebar present.
    if (!is_active_sidebar('sidebar-1')) {
        $classes[] = 'no-sidebar';
    }

    return $classes;
}
add_filter('body_class', 'ai_tech_theme_body_classes');

/**
 * Add a pingback url auto-discovery header for single posts, pages, or attachments.
 */
function ai_tech_theme_pingback_header() {
    if (is_singular() && pings_open()) {
        printf('<link rel="pingback" href="%s">', esc_url(get_bloginfo('pingback_url')));
    }
}
add_action('wp_head', 'ai_tech_theme_pingback_header');

/**
 * Adds custom meta tags for SEO.
 */
function ai_tech_theme_meta_tags() {
    global $post;
    
    if (is_singular()) {
        $excerpt = strip_tags(get_the_excerpt());
        if (empty($excerpt)) {
            $excerpt = strip_tags(wp_trim_words(get_the_content(), 55, ''));
        }
        
        echo '<meta name="description" content="' . esc_attr($excerpt) . '" />' . "\n";
        
        if (has_post_thumbnail()) {
            $thumbnail_src = wp_get_attachment_image_src(get_post_thumbnail_id(), 'large');
            echo '<meta property="og:image" content="' . esc_attr($thumbnail_src[0]) . '" />' . "\n";
        }
        
        echo '<meta property="og:title" content="' . esc_attr(get_the_title()) . '" />' . "\n";
        echo '<meta property="og:description" content="' . esc_attr($excerpt) . '" />' . "\n";
        echo '<meta property="og:url" content="' . esc_url(get_permalink()) . '" />' . "\n";
        echo '<meta property="og:type" content="article" />' . "\n";
        echo '<meta property="og:site_name" content="' . esc_attr(get_bloginfo('name')) . '" />' . "\n";
    } else {
        echo '<meta name="description" content="' . esc_attr(get_bloginfo('description')) . '" />' . "\n";
        echo '<meta property="og:title" content="' . esc_attr(get_bloginfo('name')) . '" />' . "\n";
        echo '<meta property="og:description" content="' . esc_attr(get_bloginfo('description')) . '" />' . "\n";
        echo '<meta property="og:url" content="' . esc_url(home_url('/')) . '" />' . "\n";
        echo '<meta property="og:type" content="website" />' . "\n";
        echo '<meta property="og:site_name" content="' . esc_attr(get_bloginfo('name')) . '" />' . "\n";
    }
}
add_action('wp_head', 'ai_tech_theme_meta_tags', 1); 