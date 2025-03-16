<?php get_header(); ?>

<div class="container">
    <div class="row">
        <main class="content-area col-md-8">
            <?php if (have_posts()) : ?>
                <?php while (have_posts()) : the_post(); ?>
                    <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                        <header class="entry-header">
                            <h2 class="entry-title">
                                <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                            </h2>
                            <div class="entry-meta">
                                <span class="posted-on">
                                    <?php echo get_the_date(); ?>
                                </span>
                                <span class="byline">
                                    <?php the_author(); ?>
                                </span>
                                <span class="cat-links">
                                    <?php the_category(', '); ?>
                                </span>
                            </div>
                        </header>

                        <div class="entry-content">
                            <?php if (has_post_thumbnail()) : ?>
                                <div class="post-thumbnail">
                                    <?php the_post_thumbnail('large'); ?>
                                </div>
                            <?php endif; ?>
                            
                            <?php the_excerpt(); ?>
                            
                            <a href="<?php the_permalink(); ?>" class="read-more">
                                <?php _e('더 읽기', 'ai-tech-theme'); ?>
                            </a>
                        </div>
                    </article>
                <?php endwhile; ?>
                
                <div class="pagination">
                    <?php the_posts_pagination(); ?>
                </div>
            <?php else : ?>
                <p><?php _e('게시물이 없습니다.', 'ai-tech-theme'); ?></p>
            <?php endif; ?>
        </main>
        
        <aside class="widget-area col-md-4">
            <?php get_sidebar(); ?>
        </aside>
    </div>
</div>

<?php get_footer(); ?> 