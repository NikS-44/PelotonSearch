/* eslint-disable no-undef */
/* eslint-disable no-unused-vars */

'use strict';

let searchIndex = 0;
let data = '';
let scrollEnabled = false;
let currentScrollHeight = 0;

function Copy() {
	let Url = document.getElementById('sharelink');
	Url.select();
	document.execCommand('copy');
}

function UpdateSearch() {
	const titleLivebox = $('#title').val().trim();
	const artistLivebox = $('#artist').val().trim();
	const difficultyCatChosen = $('#multdifficultycat').val();
	const typeCatChosen = $('#multtypecat').chosen().val();
	const durationChosen = $('#multDuration').chosen().val();
	const instructorChosen = $('#instructorlist').chosen().val();
	const sortbyBox = $('#sortby').val();
	let excludeArtistBox = '';
	if ($('#excludeartist').is(':checked')) {
		excludeArtistBox = 'exclude';
	} else {
		excludeArtistBox = 'include';
	}
	let  excludeTitleBox = '';
	if ($('#excludetitle').is(':checked')) {
		excludeTitleBox = 'exclude';
	} else {
		excludeTitleBox = 'include';
	}

	$.ajax({
		method: 'POST',
		url: '/PelotonSearch',
		data: {
			title: titleLivebox,
			difficulty_cat_chosen: difficultyCatChosen,
			duration_chosen: durationChosen,
			instructor_chosen: instructorChosen,
			type_cat_chosen: typeCatChosen,
			artist: artistLivebox,
			exclude_artist: excludeArtistBox,
			search_index: searchIndex,
			sort_by: sortbyBox,
			exclude_title: excludeTitleBox
		},
		success: (res) => {
			let stopSearch = data;
			$.each(res, (index, value) => {
				let diffParsed = value.Difficulty_Category;
				// Removing the any spaces in the category name so we can use it as a class tag
				if (value.Difficulty_Category === 'Very Easy') {
					diffParsed = 'VeryEasy';
				}
				if (value.Difficulty_Category === 'Very Hard') {
					diffParsed = 'VeryHard';
				}
				// Creating the individual class boxes
				if (value.Difficulty_Category === 'Power Zone') {
					data +=
					    "<div class='myDiv box-shadow-hover pointer'><a href=" +
						value.Workout_Link +
						'><div class=class-picture><img src=https://res.cloudinary.com/peloton-cycle/image/fetch/c_scale,dpr_1.0,f_auto,q_auto,w_352/' +
						value.Thumbnail +
						' height=232 width=352 ><div class=class-title><h2>' +
						value.Title +
						'</h2></div><div class=class-date><h4>' +
						value.Release_Date +
						'</div></h4><div class=class-instructor><h4>' +
						value.Instructor +
						'</h4></div><div class=class-difficulty><h5>Difficulty: ' +
						value.Peloton_Difficulty_Rating +
						'</div></h5><div class=class-rating><h5>'+
						value.User_Rating +
						'% <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-hand-thumbs-up" viewBox="0 0 16 16"><path d="M8.864.046C7.908-.193 7.02.53 6.956 1.466c-.072 1.051-.23 2.016-.428 2.59-.125.36-.479 1.013-1.04 1.639-.557.623-1.282 1.178-2.131 1.41C2.685 7.288 2 7.87 2 8.72v4.001c0 .845.682 1.464 1.448 1.545 1.07.114 1.564.415 2.068.723l.048.03c.272.165.578.348.97.484.397.136.861.217 1.466.217h3.5c.937 0 1.599-.477 1.934-1.064a1.86 1.86 0 0 0 .254-.912c0-.152-.023-.312-.077-.464.201-.263.38-.578.488-.901.11-.33.172-.762.004-1.149.069-.13.12-.269.159-.403.077-.27.113-.568.113-.857 0-.288-.036-.585-.113-.856a2.144 2.144 0 0 0-.138-.362 1.9 1.9 0 0 0 .234-1.734c-.206-.592-.682-1.1-1.2-1.272-.847-.282-1.803-.276-2.516-.211a9.84 9.84 0 0 0-.443.05 9.365 9.365 0 0 0-.062-4.509A1.38 1.38 0 0 0 9.125.111L8.864.046zM11.5 14.721H8c-.51 0-.863-.069-1.14-.164-.281-.097-.506-.228-.776-.393l-.04-.024c-.555-.339-1.198-.731-2.49-.868-.333-.036-.554-.29-.554-.55V8.72c0-.254.226-.543.62-.65 1.095-.3 1.977-.996 2.614-1.708.635-.71 1.064-1.475 1.238-1.978.243-.7.407-1.768.482-2.85.025-.362.36-.594.667-.518l.262.066c.16.04.258.143.288.255a8.34 8.34 0 0 1-.145 4.725.5.5 0 0 0 .595.644l.003-.001.014-.003.058-.014a8.908 8.908 0 0 1 1.036-.157c.663-.06 1.457-.054 2.11.164.175.058.45.3.57.65.107.308.087.67-.266 1.022l-.353.353.353.354c.043.043.105.141.154.315.048.167.075.37.075.581 0 .212-.027.414-.075.582-.05.174-.111.272-.154.315l-.353.353.353.354c.047.047.109.177.005.488a2.224 2.224 0 0 1-.505.805l-.353.353.353.354c.006.005.041.05.041.17a.866.866 0 0 1-.121.416c-.165.288-.503.56-1.066.56z"/></svg>'+
						'</h5></div></div>';
				} else {
					data +=
						"<div class='myDiv box-shadow-hover pointer'><a href=" +
						value.Workout_Link +
						'><div class=class-picture><img src=https://res.cloudinary.com/peloton-cycle/image/fetch/c_scale,dpr_1.0,f_auto,q_auto,w_352/' +
						value.Thumbnail +
						' height=232 width=352 ><div class=class-title><h2>' +
						value.Title +
						'</h2></div><div class=class-date><h4>' +
						value.Release_Date +
						'</div></h4><div class=class-instructor><h4>' +
						value.Instructor +
						'</h4></div><div class=class-output><h5>' +
						value.Expected_Min +
						' kJ - ' +
						value.Expected_Max +
						' kJ' +
						'    ·   <b class=' +
						diffParsed +
						' >▊' +
						value.Difficulty_Category +
						'</b></div></h5><div class=class-difficulty><h5>Difficulty: ' +
						value.Peloton_Difficulty_Rating +
						'</div></h5><div class=class-rating><h5>'+
						value.User_Rating +
						'% <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-hand-thumbs-up thumbs-up" viewBox="0 0 16 16"><path d="M8.864.046C7.908-.193 7.02.53 6.956 1.466c-.072 1.051-.23 2.016-.428 2.59-.125.36-.479 1.013-1.04 1.639-.557.623-1.282 1.178-2.131 1.41C2.685 7.288 2 7.87 2 8.72v4.001c0 .845.682 1.464 1.448 1.545 1.07.114 1.564.415 2.068.723l.048.03c.272.165.578.348.97.484.397.136.861.217 1.466.217h3.5c.937 0 1.599-.477 1.934-1.064a1.86 1.86 0 0 0 .254-.912c0-.152-.023-.312-.077-.464.201-.263.38-.578.488-.901.11-.33.172-.762.004-1.149.069-.13.12-.269.159-.403.077-.27.113-.568.113-.857 0-.288-.036-.585-.113-.856a2.144 2.144 0 0 0-.138-.362 1.9 1.9 0 0 0 .234-1.734c-.206-.592-.682-1.1-1.2-1.272-.847-.282-1.803-.276-2.516-.211a9.84 9.84 0 0 0-.443.05 9.365 9.365 0 0 0-.062-4.509A1.38 1.38 0 0 0 9.125.111L8.864.046zM11.5 14.721H8c-.51 0-.863-.069-1.14-.164-.281-.097-.506-.228-.776-.393l-.04-.024c-.555-.339-1.198-.731-2.49-.868-.333-.036-.554-.29-.554-.55V8.72c0-.254.226-.543.62-.65 1.095-.3 1.977-.996 2.614-1.708.635-.71 1.064-1.475 1.238-1.978.243-.7.407-1.768.482-2.85.025-.362.36-.594.667-.518l.262.066c.16.04.258.143.288.255a8.34 8.34 0 0 1-.145 4.725.5.5 0 0 0 .595.644l.003-.001.014-.003.058-.014a8.908 8.908 0 0 1 1.036-.157c.663-.06 1.457-.054 2.11.164.175.058.45.3.57.65.107.308.087.67-.266 1.022l-.353.353.353.354c.043.043.105.141.154.315.048.167.075.37.075.581 0 .212-.027.414-.075.582-.05.174-.111.272-.154.315l-.353.353.353.354c.047.047.109.177.005.488a2.224 2.224 0 0 1-.505.805l-.353.353.353.354c.006.005.041.05.041.17a.866.866 0 0 1-.121.416c-.165.288-.503.56-1.066.56z"/></svg>'+
						'</h5></div></div>';
				}
				data += '<h4 class=class-artists>Artists: ';
				const songJSON = JSON.parse(value.Songs);
				for (let i = 0; i < songJSON.length; i++) {
					if (i === 0) {
						data += songJSON[i].Artist;
					} else {
						data += `, ${songJSON[i].Artist}`;
					}
				}
				data += '</h4></div></a><br>';
			});
			$('#datalist').html(data);
			if (stopSearch === data) {
				scrollEnabled = false;
			}

			/* Create Saved Search Link based on current search parameters */
			let shareableLink = `${window.location.protocol}//${window.location.host}/?`;
			if (titleLivebox) {
				shareableLink += `title=${encodeURIComponent(titleLivebox)}&`;
			}
			if (artistLivebox) {
				shareableLink += `artist=${encodeURIComponent(artistLivebox)}&`;
			}
			if (durationChosen && durationChosen.length) {
				for (let j = 0; j < durationChosen.length; j++) {
					shareableLink += `duration=${encodeURIComponent(durationChosen[j])}&`;
				}
			}
			if (difficultyCatChosen && difficultyCatChosen.length) {
				for (let j = 0; j < difficultyCatChosen.length; j++) {
					shareableLink += `difficulty=${encodeURIComponent(
						difficultyCatChosen[j]
					)}&`;
				}
			}
			if (typeCatChosen && typeCatChosen.length) {
				for (let j = 0; j < typeCatChosen.length; j++) {
					shareableLink += `category=${encodeURIComponent(typeCatChosen[j])}&`;
				}
			}
			if (excludeArtistBox === 'exclude') {
				shareableLink += `excludeartist=${encodeURIComponent(
					excludeArtistBox
				)}&`;
			}
			if (excludeTitleBox === 'exclude') {
				shareableLink += `excludetitle=${encodeURIComponent(
					excludeTitleBox
				)}&`;
			}
			if (instructorChosen && instructorChosen.length) {
				for (let j = 0; j < instructorChosen.length; j++) {
					shareableLink += `instructor=${encodeURIComponent(
						instructorChosen[j]
					)}&`;
				}
			}
			if (sortbyBox) {
				shareableLink += `sortby=${encodeURIComponent(sortbyBox)}&`;
			}
			shareableLink += 'autosubmit=1';
			$('#sharelink').html(shareableLink);
		},
	});
}

document.addEventListener('DOMContentLoaded', () => {
	/* Chosen Initialization */
	$('.chosen-select').chosen();
	$('.chosen-select2').chosen();
	$('.chosen-select3').chosen();
	$('.chosen-select4').chosen();

	/* Pulling the search parameters from the URL. If autosubmit is enabled in the URL,
       it will also initiate the search on page load */
	let urlParams = new URLSearchParams(window.location.search);
	let titleParam = document.getElementById('title');
	let artistParam = document.getElementById('artist');
	let sortByParam = document.getElementById('sortby');
	sortByParam.value = 'Newest';
	let excludeArtistParam = document.getElementById('excludeartist');
	let excludeTitleParam = document.getElementById('excludetitle');
	if (urlParams.get('title')) {
		titleParam.value = urlParams.get('title');
	}
	if (urlParams.get('artist')) {
		artistParam.value = urlParams.get('artist');
	}
	if (urlParams.get('excludeartist')) {
		excludeArtistParam.checked = true;
	}
	if (urlParams.get('excludetitle')) {
		excludeTitleParam.checked = true;
	}
	if (urlParams.get('sortby')) {
		sortByParam.value = urlParams.get('sortby');
	}
	$('.chosen-select4')
		.val(urlParams.getAll('difficulty'))
		.trigger('chosen:updated');
	$('.chosen-select3')
		.val(urlParams.getAll('category'))
		.trigger('chosen:updated');
	$('.chosen-select2')
		.val(urlParams.getAll('duration'))
		.trigger('chosen:updated');
	$('.chosen-select')
		.val(urlParams.getAll('instructor'))
		.trigger('chosen:updated');
	if (urlParams.get('autosubmit') !== '0') {
		setTimeout(function () {
			document.getElementById('submitBtn').click();
		}, 100);
	}

	/* Infinite scrolling implementation - Loads 10 new users when the bottom of the page is reached */
	window.addEventListener('scroll', () => {
		const scrollHeight = $(document).height();
		const scrollPos = Math.floor($(window).height() + $(window).scrollTop());
		const isBottom = scrollHeight - 800 < scrollPos;
		if (isBottom && currentScrollHeight < scrollHeight && scrollEnabled) {
			searchIndex += 36;
			UpdateSearch();
			currentScrollHeight = scrollHeight;
		}
	});

	/* New Search query when user or other JS code clicks Submit  */
	document.getElementById('submitBtn').addEventListener('click', () => {
		data = '';
		searchIndex = 0;
		currentScrollHeight = 0;
		scrollEnabled = true;
		UpdateSearch();
	});
});
