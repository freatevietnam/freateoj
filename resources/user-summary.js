// User Summary Modal - Hover on desktop, Click on mobile
$(document).ready(function() {
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    var hoverTimeout;
    var hideTimeout;
    var currentUsername = null;
    
    // Create modal HTML - positioned tooltip style
    var modalHTML = `
        <div id="user-summary-tooltip" class="user-summary-tooltip" style="display: none;">
            <div class="user-summary-content">
                <div class="user-summary-header">
                    <div class="user-summary-avatar">
                        <img src="" alt="" id="user-summary-avatar">
                    </div>
                    <div class="user-summary-info">
                        <h3 id="user-summary-display-name"></h3>
                        <span id="user-summary-username" class="user-summary-username"></span>
                        <span id="user-summary-rank" class="user-summary-rank"></span>
                    </div>
                    <div class="user-summary-badges" id="user-summary-badges"></div>
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
                        <span class="stat-value" id="user-summary-pp"></span>
                        <span class="stat-label">PP</span>
                    </div>
                </div>
                <div class="user-summary-activity">
                    <div class="activity-header" id="user-summary-activity-header"></div>
                    <div class="activity-grid" id="user-summary-activity-grid"></div>
                </div>
                <div class="user-summary-actions">
                    <a id="user-summary-profile-btn" href="" class="btn btn-primary">View Profile</a>
                </div>
            </div>
            <div class="user-summary-arrow"></div>
        </div>
    `;
    
    $('body').append(modalHTML);
    
    // Check if link is a user link
    function isUserLink($link) {
        var href = $link.attr('href');
        if (!href) return false;
        
        var match = href.match(/\/user\/([^\/]+)\/?$/);
        if (!match) return false;
        
        // Don't show modal for certain links
        if ($link.hasClass('no-modal') || 
            $link.hasClass('btn-top-bar') ||
            $link.closest('.user-summary-tooltip').length ||
            $link.closest('.user-summary-modal').length) {
            return false;
        }
        
        return match[1];
    }
    
    // Position tooltip below the hovered element
    function positionTooltip($link) {
        var $tooltip = $('#user-summary-tooltip');
        var linkRect = $link[0].getBoundingClientRect();
        var tooltipWidth = $tooltip.outerWidth();
        var tooltipHeight = $tooltip.outerHeight();
        
        // Calculate position
        var left = linkRect.left + (linkRect.width / 2) - (tooltipWidth / 2);
        var top = linkRect.bottom + 10;
        
        // Keep within viewport
        if (left < 10) left = 10;
        if (left + tooltipWidth > $(window).width() - 10) {
            left = $(window).width() - tooltipWidth - 10;
        }
        
        // If would go below viewport, show above
        if (top + tooltipHeight > $(window).height() + $(window).scrollTop() - 10) {
            top = linkRect.top - tooltipHeight - 10;
            $tooltip.addClass('above');
        } else {
            $tooltip.removeClass('above');
        }
        
        $tooltip.css({
            left: left + 'px',
            top: top + 'px'
        });
    }
    
    // Render badges
    function renderBadges(badges, displayBadge) {
        var $badges = $('#user-summary-badges');
        $badges.empty();
        
        // Show display badge first (the one shown next to username on profile)
        if (displayBadge && displayBadge.mini) {
            $badges.append('<img class="user-summary-badge" src="' + displayBadge.mini + '" alt="' + displayBadge.name + '" title="' + displayBadge.name + '">');
        }
        
        // Then show other badges
        if (badges && badges.length > 0) {
            badges.forEach(function(badge) {
                // Skip if it's the same as display badge
                if (displayBadge && badge.name === displayBadge.name) return;
                $badges.append('<img class="user-summary-badge" src="' + (badge.mini || badge.full_size) + '" alt="' + badge.name + '" title="' + badge.name + '">');
            });
        }
    }
    
    // Draw submission activity grid
    function drawActivityGrid(submissionActivity) {
        var $grid = $('#user-summary-activity-grid');
        $grid.empty();
        
        var activityLevels = 5;
        var currentYear = new Date().getFullYear();
        var today = new Date();
        var oneYearAgo = new Date(today);
        oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
        
        // Get max activity for normalization
        var maxActivity = 1;
        for (var date in submissionActivity) {
            if (submissionActivity[date] > maxActivity) {
                maxActivity = submissionActivity[date];
            }
        }
        
        // Calculate total submissions
        var totalSubmissions = 0;
        for (var date in submissionActivity) {
            totalSubmissions += submissionActivity[date];
        }
        
        // Update header
        $('#user-summary-activity-header').text(totalSubmissions + ' submissions in the past year');
        
        // Create 52 weeks x 7 days grid
        var startDate = new Date(oneYearAgo);
        startDate.setDate(startDate.getDate() - startDate.getDay()); // Start from Sunday
        
        var weeks = 53;
        var days = 7;
        
        // Create grid container
        var $table = $('<table class="activity-table"></table>');
        
        // Day labels
        var dayLabels = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
        var $headerRow = $('<tr></tr>');
        $headerRow.append('<td class="day-label"></td>');
        for (var w = 0; w < weeks; w++) {
            $headerRow.append('<td class="week-header"></td>');
        }
        $table.append($headerRow);
        
        // Activity rows
        for (var d = 0; d < days; d++) {
            var $row = $('<tr></tr>');
            $row.append('<td class="day-label">' + dayLabels[d] + '</td>');
            
            for (var w = 0; w < weeks; w++) {
                var cellDate = new Date(startDate);
                cellDate.setDate(cellDate.getDate() + (w * 7) + d);
                
                var isodate = cellDate.toISOString().split('T')[0];
                var activity = submissionActivity[isodate] || 0;
                var level = activity > 0 ? Math.ceil((activity / maxActivity) * (activityLevels - 1)) : 0;
                
                var $cell = $('<td class="activity-cell"></td>');
                var $div = $('<div class="activity-' + level + '"></div>');
                
                if (activity > 0) {
                    $div.attr('title', activity + ' submissions on ' + cellDate.toLocaleDateString());
                }
                
                $cell.append($div);
                $row.append($cell);
            }
            
            $table.append($row);
        }
        
        $grid.append($table);
        
        // Add legend
        var $legend = $('<div class="activity-legend"></div>');
        $legend.append('<span class="legend-text">Less</span>');
        for (var i = 0; i < activityLevels; i++) {
            $legend.append('<div class="activity-cell"><div class="activity-' + i + '"></div></div>');
        }
        $legend.append('<span class="legend-text">More</span>');
        $grid.append($legend);
    }
    
    // Show user summary tooltip
    function showUserSummary(username, $link) {
        if (currentUsername === username && $('#user-summary-tooltip').is(':visible')) {
            return;
        }
        
        currentUsername = username;
        
        // Clear any pending hide
        clearTimeout(hideTimeout);
        
        $.ajax({
            url: '/widgets/user-summary/' + username + '/',
            method: 'GET',
            beforeSend: function() {
                $('#user-summary-display-name').text('Loading...');
                positionTooltip($link);
                $('#user-summary-tooltip').show();
            },
            success: function(data) {
                // Update tooltip content
                $('#user-summary-display-name').text(data.display_name || data.username);
                $('#user-summary-username').text('@' + data.username);
                $('#user-summary-rank').text(data.rank).attr('class', 'user-summary-rank rank-' + data.rank.toLowerCase());
                
                $('#user-summary-rating').text(data.rating || '-');
                $('#user-summary-solved').text(data.problems_solved || 0);
                var pp = parseFloat(data.performance_points) || 0;
                $('#user-summary-pp').text(pp.toFixed(2));
                
                if (data.avatar_url) {
                    $('#user-summary-avatar').attr('src', data.avatar_url).show();
                } else {
                    $('#user-summary-avatar').hide();
                }
                
                $('#user-summary-profile-btn').attr('href', data.profile_url);
                
                // Render badges
                renderBadges(data.badges, data.display_badge);
                
                // Draw activity grid
                drawActivityGrid(data.submission_activity || {});
                
                // Reposition after content loaded
                positionTooltip($link);
            },
            error: function() {
                $('#user-summary-tooltip').hide();
                currentUsername = null;
            }
        });
    }
    
    // Hide user summary tooltip
    function hideUserSummary() {
        hideTimeout = setTimeout(function() {
            $('#user-summary-tooltip').hide();
            currentUsername = null;
        }, 300);
    }
    
    // Desktop: Hover events
    if (!isMobile) {
        $(document).on('mouseenter', 'a[href*="/user/"]', function() {
            var $link = $(this);
            var username = isUserLink($link);
            
            if (username) {
                clearTimeout(hideTimeout);
                hoverTimeout = setTimeout(function() {
                    showUserSummary(username, $link);
                }, 200);
            }
        });
        
        $(document).on('mouseleave', 'a[href*="/user/"]', function() {
            clearTimeout(hideTimeout);
            hideUserSummary();
        });
        
        // Keep tooltip visible when hovering over it
        $(document).on('mouseenter', '#user-summary-tooltip', function() {
            clearTimeout(hideTimeout);
        });
        
        $(document).on('mouseleave', '#user-summary-tooltip', function() {
            hideUserSummary();
        });
    }
    
    // Mobile: Click events
    if (isMobile) {
        $(document).on('click', 'a[href*="/user/"]', function(e) {
            var $link = $(this);
            var username = isUserLink($link);
            
            if (username) {
                e.preventDefault();
                showUserSummary(username, $link);
            }
        });
        
        // Close on tap outside
        $(document).on('click', function(e) {
            if (!$(e.target).closest('#user-summary-tooltip, a[href*="/user/"]').length) {
                $('#user-summary-tooltip').hide();
                currentUsername = null;
            }
        });
    }
    
    // Close on escape key
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape') {
            $('#user-summary-tooltip').hide();
            currentUsername = null;
        }
    });
    
    // Reposition on scroll/resize
    $(window).on('scroll resize', function() {
        if ($('#user-summary-tooltip').is(':visible')) {
            var $currentLink = $('a[href*="/user/"]:hover').first();
            if ($currentLink.length) {
                positionTooltip($currentLink);
            }
        }
    });
});
