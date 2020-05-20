
// Blocks
casper.thenOpen('http://localhost:9001/styleguide/components_-_blocks.html').
	then(function() {	
		phantomcss.screenshot('.block', 'blocks');
	}).
	then(function() {
		phantomcss.screenshot('.block__issue', 'block__issue');
	});

// Main image
casper.thenOpen('http://localhost:9001/styleguide/components_-_images.html').
	then(function() {
		phantomcss.screenshot('.banner-art-wrapper', 'banner-art');
	});

// Announcements
casper.thenOpen('http://localhost:9001/styleguide/components_-_announcements.html').
	then(function() {
		phantomcss.screenshot('.announcement', 'announcments');
	});

// Footnotes
casper.thenOpen('http://localhost:9001/styleguide/components_-_footnotes.html').
	then(function() {
		phantomcss.screenshot('.article-body', 'footnotes');
	});

// Forms
casper.thenOpen('http://localhost:9001/styleguide/components_-_forms.html').
	then(function() {
		phantomcss.screenshot('#mc_embed_signup', 'signup-form');
	});

// pagination
casper.thenOpen('http://localhost:9001/styleguide/components_-_pagination.html').
	then(function() {
		phantomcss.screenshot('.pagination', 'pagination');
	})

// toc
casper.thenOpen('http://localhost:9001/styleguide/components_-_toc.html').
	then(function() {
		phantomcss.screenshot('.toc', 'table-of-contents');
	});
