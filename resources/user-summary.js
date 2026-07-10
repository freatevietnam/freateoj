// User Summary Modal
$(document).ready(function() {
    // Create modal HTML
    var modalHTML = `
        <div id="user-summary-modal" class="user-summary-modal" style="display: none;">
            <div class="user-summary-overlay"></div>
            <div class="user-summary-content">
                <button class="user-summary-close">&times;</button>
                <div class="user-summary-header">
                    <div class="user-summary-avatar">
                        <img src="" alt="" id="user-summary-avatar">
                    </div>
                    <div class="user-summary-info">
                        <h3 id="user-summary-display-name"></h3>
                        <span id="user-summary-username" class="user-summary-username"></span>
                        <span id="user-summary-rank" class="user-summary-rank"></span>
                    </div>
                </div>
                <div class="user-summary-stats">
                    <div class="user-summary-stat">
                        <span class="stat-value" id="user-summary-rating"></span>
                        <span class="stat-label">Rating</span>
                    </div>
                    <div class="user-summary-stat">
                        <span class="stat-value" id="user-summary-solved"></span>
                        <span class="stat-label">Solved</span>
                    </div>
                    <div class="user-summary-stat">
                        <span class="stat-value" id="user-summary-attempted"></span>
                        <span class="stat-label">Attempted</span>
                    </div>
                    <div class="user-summary-stat">
                        <span class="stat-value" id="user-summary-pp"></span>
                        <span class="stat-label">PP</span>
                    </div>
                </div>
                <div class="user-summary-meta">
                    <div class="user-summary-meta-item">
                        <i class="fa fa-calendar"></i>
                        <span>Joined: </span>
                        <span id="user-summary-join-date"></span>
                    </div>
                    <div class="user-summary-meta-item">
                        <i class="fa fa-clock"></i>
                        <span>Last login: </span>
                        <span id="user-summary-last-login"></span>
                    </div>
                </div>
                <div class="user-summary-actions">
                    <a id="user-summary-profile-btn" href="" class="btn btn-primary">View Profile</a>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(modalHTML);
    
    // Handle user link clicks
    $(document).on('click', 'a[href*="/user/"]', function(e) {
        var href = $(this).attr('href');
        var match = href.match(/\/user\/([^\/]+)\/?$/);
        
        if (match) {
            var username = match[1];
            
            // Don't show modal for certain links
            if ($(this).hasClass('no-modal') || 
                $(this).hasClass('btn-top-bar') ||
                $(this).closest('.user-summary-modal').length) {
                return;
            }
            
            e.preventDefault();
            showUserSummary(username, $(this));
        }
    });
    
    // Show user summary modal
    function showUserSummary(username, $link) {
        $.ajax({
            url: '/widgets/user-summary/' + username + '/',
            method: 'GET',
            beforeSend: function() {
                // Show loading state
                $('#user-summary-display-name').text('Loading...');
                $('#user-summary-modal').show();
            },
            success: function(data) {
                // Update modal content
                $('#user-summary-display-name').text(data.display_name || data.username);
                $('#user-summary-username').text('@' + data.username);
                $('#user-summary-rank').text(data.rank).attr('class', 'user-summary-rank rank-' + data.rank.toLowerCase());
                
                $('#user-summary-rating').text(data.rating || '-');
                $('#user-summary-solved').text(data.problems_solved || 0);
                $('#user-summary-attempted').text(data.problems_attempted || 0);
                $('#user-summary-pp').text(data.performance_points || 0);
                
                $('#user-summary-join-date').text(data.join_date || '-');
                $('#user-summary-last-login').text(data.last_login || '-');
                
                if (data.avatar_url) {
                    $('#user-summary-avatar').attr('src', data.avatar_url).show();
                } else {
                    $('#user-summary-avatar').hide();
                }
                
                $('#user-summary-profile-btn').attr('href', data.profile_url);
                
                // Show modal
                $('#user-summary-modal').fadeIn(200);
            },
            error: function() {
                // Fallback: redirect to profile page
                window.location.href = '/user/' + username + '/';
            }
        });
    }
    
    // Close modal
    $(document).on('click', '.user-summary-close, .user-summary-overlay', function() {
        $('#user-summary-modal').fadeOut(200);
    });
    
    // Close on escape key
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape') {
            $('#user-summary-modal').fadeOut(200);
        }
    });
});
