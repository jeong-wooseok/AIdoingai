<?php
/**
 * AI Tech Theme Theme Customizer
 */

/**
 * Add postMessage support for site title and description for the Theme Customizer.
 *
 * @param WP_Customize_Manager $wp_customize Theme Customizer object.
 */
function ai_tech_theme_customize_register($wp_customize) {
    $wp_customize->get_setting('blogname')->transport         = 'postMessage';
    $wp_customize->get_setting('blogdescription')->transport  = 'postMessage';
    $wp_customize->get_setting('header_textcolor')->transport = 'postMessage';

    if (isset($wp_customize->selective_refresh)) {
        $wp_customize->selective_refresh->add_partial(
            'blogname',
            array(
                'selector'        => '.site-title a',
                'render_callback' => 'ai_tech_theme_customize_partial_blogname',
            )
        );
        $wp_customize->selective_refresh->add_partial(
            'blogdescription',
            array(
                'selector'        => '.site-description',
                'render_callback' => 'ai_tech_theme_customize_partial_blogdescription',
            )
        );
    }

    // 테마 색상 설정
    $wp_customize->add_setting(
        'theme_primary_color',
        array(
            'default'           => '#3498db',
            'sanitize_callback' => 'sanitize_hex_color',
            'transport'         => 'postMessage',
        )
    );

    $wp_customize->add_control(
        new WP_Customize_Color_Control(
            $wp_customize,
            'theme_primary_color',
            array(
                'label'    => __('Primary Color', 'ai-tech-theme'),
                'section'  => 'colors',
                'settings' => 'theme_primary_color',
            )
        )
    );

    // 소셜 미디어 링크 섹션
    $wp_customize->add_section(
        'social_links',
        array(
            'title'    => __('Social Media Links', 'ai-tech-theme'),
            'priority' => 120,
        )
    );

    // Twitter
    $wp_customize->add_setting(
        'social_twitter',
        array(
            'default'           => '',
            'sanitize_callback' => 'esc_url_raw',
        )
    );

    $wp_customize->add_control(
        'social_twitter',
        array(
            'label'    => __('Twitter URL', 'ai-tech-theme'),
            'section'  => 'social_links',
            'type'     => 'url',
        )
    );

    // Facebook
    $wp_customize->add_setting(
        'social_facebook',
        array(
            'default'           => '',
            'sanitize_callback' => 'esc_url_raw',
        )
    );

    $wp_customize->add_control(
        'social_facebook',
        array(
            'label'    => __('Facebook URL', 'ai-tech-theme'),
            'section'  => 'social_links',
            'type'     => 'url',
        )
    );

    // Instagram
    $wp_customize->add_setting(
        'social_instagram',
        array(
            'default'           => '',
            'sanitize_callback' => 'esc_url_raw',
        )
    );

    $wp_customize->add_control(
        'social_instagram',
        array(
            'label'    => __('Instagram URL', 'ai-tech-theme'),
            'section'  => 'social_links',
            'type'     => 'url',
        )
    );
}
add_action('customize_register', 'ai_tech_theme_customize_register');

/**
 * Render the site title for the selective refresh partial.
 *
 * @return void
 */
function ai_tech_theme_customize_partial_blogname() {
    bloginfo('name');
}

/**
 * Render the site tagline for the selective refresh partial.
 *
 * @return void
 */
function ai_tech_theme_customize_partial_blogdescription() {
    bloginfo('description');
}

/**
 * Binds JS handlers to make Theme Customizer preview reload changes asynchronously.
 */
function ai_tech_theme_customize_preview_js() {
    wp_enqueue_script('ai-tech-theme-customizer', get_template_directory_uri() . '/js/customizer.js', array('customize-preview'), '20151215', true);
}
add_action('customize_preview_init', 'ai_tech_theme_customize_preview_js'); 