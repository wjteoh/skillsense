jQuery(document).ready(function($){
	//open the lateral panel
	$('.cd-btn').on('click', function(event){
		event.preventDefault();
		$('.cd-panel').addClass('is-visible');
	});
	//clode the lateral panel
	$('.cd-panel').on('click', function(event){
		if( $(event.target).is('.cd-panel') || $(event.target).is('#close') ) { 
			$('.cd-panel').removeClass('is-visible');
			event.preventDefault();
		}
	});
	
	//Minimise the lateral panel
	
	$('.cd-btn2').on('click', function(event){
		event.preventDefault();
		$('.cd-panel2').addClass('is-visible');
	});
	
	$('.cd-btn3').on('click', function(event){
		event.preventDefault();
		$('.cd-panel2').addClass('is-visible2');
	});
	
	//clode the lateral panel
	$('.cd-panel2').on('click', function(event){
		if( $(event.target).is('.cd-panel2') || $(event.target).is('#close1') ) { 
			
			$('.cd-panel2').removeClass('is-visible2');
			$('.cd-panel2').removeClass('is-visible');
			event.preventDefault();
		}
	});
	
	$('.cd-panel2').on('click', function(event){
		if( $(event.target).is('.cd-panel2') || $(event.target).is('#close2') ) { 
			
			$('.cd-panel2').removeClass('is-visible2');
			event.preventDefault();
		}
	});
	
});