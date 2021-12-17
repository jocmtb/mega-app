
    // Strip whitespace from Ace Editor text
	var p = document.getElementsByClassName("editor");
	for (i = 0; i < p.length; i++) {
		p[i].textContent = p[i].textContent.replace(/^\s+/mg, "");
	};

	// Initialize Ace Editor for all .editor elements
    var editor;
    $('.editor').each(function( index ) {
    	editor = ace.edit(this);

    	editor.setOptions({
	    	readOnly: true,
	    	showLineNumbers: false,
	    	showGutter: false,
	    	showPrintMargin: false,
	    });
		editor.setTheme("ace/theme/chrome");
    });


    // Initialize collapse button and collapsible accordion
    $(".button-collapse").sideNav();
    $('.collapsible').collapsible();


    // Open parent collapsibles when child collapsible is opened
    $('[data-click]').on('click', function(e) {
        var el = $($(this).attr('href'));
        var oneUp = $(el).closest('.collapsible-body').prev('.collapsible-header');
        var twoUp = $(oneUp).closest('.collapsible-body').prev('.collapsible-header');

        $(el).trigger('click');
        $.each([oneUp, twoUp], function(i, val) {
            if (!$(val).hasClass('active'))
                $(val).trigger('click');
        });

        // close sidenav on link click
        $(this).sideNav('hide');
    });


    // Stop collapse event from actions clicked inside collapsible headers
    $(".not-collapse").on("click", function(e) { e.stopPropagation(); });

    // Expand or Collapse sections by trigerring a click
    $('.expand i').on('click', function(e) {
    	var parent, all, el;

    	el = $(this);
		parent = el.closest('.collapsible-header');
		all = parent.next('.collapsible-body')
				    .find('.collapsible-header');

		if ( el.closest('.side-nav').length !== 0 ) {
			headers = $('.side-nav .collapsible-header');

			if ( el.hasClass('all') && !headers.hasClass('active'))
				headers.trigger('click');
			else if ( el.hasClass('none') && headers.hasClass('active') )
				headers.trigger('click');
		}

		// check if the click is to expand all sections
     	else if ( el.hasClass('all') ) {
    		all.each( function() {
    			if ( !$(this).hasClass('active') )
    				$(this).trigger('click');
    		});
    		if ( !parent.hasClass('active') )
    			parent.trigger('click');
    	}

    	// check if the click is to collapse all sections
    	else if ( el.hasClass('none') ) {
    		all.each( function() {
    			if ( $(this).hasClass('active') )
    				$(this).trigger('click');
    		});
    		// close the parent collapse section if it's open
    		if ( parent.hasClass('active') )
    			parent.trigger('click');
    	}
    });


	// Toggle scrollToTop button visibility based on scroll
	$(document).ready(function(){
		//Check to see if the window is top if not then display button
		$(window).scroll(function(){
			if ($(this).scrollTop() > 100)
				$('.scrollToTop').fadeIn();
			else
				$('.scrollToTop').fadeOut();
		});
		//Click event to scroll to top
		$('.scrollToTop').click(function(){
			$('html, body').animate({scrollTop : 0},800);
			return false;
		});
	});


	// Setup custom collapse sections
	$('[data-function="toggler"]').on('click', function (e) {
	    var el = $(this);
	    var header = el.closest('.collapsible-header');
		var collapse;

		// check the data-target, find that first child, then
		// assign for toggling
	    if (el.attr('data-target') == 'descr') {
	    	if (header.next('.collapsible-body').length !== 0){
	    		console.log(header.next('.collapsible-body'))
	    		collapse = header.next('.collapsible-body').find('.descr').first();
	    	}
	    	else
	    		collapse = header.next('.descr');
	    }
	    else if (el.attr('data-target') == 'meta')
	    	collapse = header.next('.collapsible-body').find('.meta').first();

	    if (!header.hasClass('active'))
	    	header.trigger('click');

     	collapse.slideToggle();
	});
