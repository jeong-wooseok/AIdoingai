<?php
if (!is_active_sidebar('sidebar-1')) {
    return;
}
?>

<div class="sidebar">
    <?php dynamic_sidebar('sidebar-1'); ?>
</div> 