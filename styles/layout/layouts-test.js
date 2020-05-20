
casper.thenOpen('http://localhost:9001/styleguide/layout_-_articles.html').
	then(function() {
		phantomcss.screenshot('.article-aside', 'article-aside');
	}).
	then(function() {
		phantomcss.screenshot('.article-body', 'article-body');
	}).
	then(function() {
		phantomcss.screenshot('.article-header', 'article-header');
	});

casper.thenOpen('http://localhost:9001/styleguide/layout_-_footer.html').
	then(function() {
		phantomcss.screenshot('.contrivers-footer', 'footer');
	});

casper.thenOpen('http://localhost:9001/styleguide/layout_-_header.html').
	then(function() {
		phantomcss.screenshot('.contrivers-header', 'header');
	});

casper.thenOpen('http://localhost:9001/styleguide/layout_-_navbar.html').
	then(function() {
		phantomcss.screenshot('.contriversNav', 'navbar');
	});


// Main Page Example
casper.thenOpen('http://localhost:9001/styleguide/examples_-_index.html').
	then(function() {
		phantomcss.screenshot('div#container', 'main-page-example');
	});
