/* eslint-disable no-undef */
/* eslint-disable no-unused-vars */

"use strict";

let searchIndex = 0;
let data = "";
let scrollEnabled = false;
let currentScrollHeight = 0;

function Copy() {
  let Url = document.getElementById("sharelink");
  Url.select();
  document.execCommand("copy");
}

function UpdateSearch(){
    const titleLivebox = $("#title").val();
    const artistLivebox = $("#artist").val();
    const difficultyCatChosen = $("#multdifficultycat").val();
    const typeCatChosen = $("#multtypecat").chosen().val();
    const durationChosen = $("#multDuration").chosen().val();
    const instructorChosen = $("#instructorlist").chosen().val();
    let excludeArtistBox = "";
    if ($("#excludeartist").is(":checked")){
        excludeArtistBox = "exclude";
    }
    else{
        excludeArtistBox = "include";
    }

    $.ajax({
        method:"POST",
        url:"/PelotonSearch",
        data:{title:titleLivebox, difficulty_cat_chosen:difficultyCatChosen, duration_chosen:durationChosen,
              instructor_chosen:instructorChosen, type_cat_chosen:typeCatChosen, artist:artistLivebox,
              exclude_artist:excludeArtistBox, search_index:searchIndex},
        success:(res) => {
            let stopSearch = data;
            $.each(res,(index,value) => {
                let diffParsed = value.Difficulty_Category;
                // Removing the any spaces in the category name so we can use it as a class tag
                if (value.Difficulty_Category === "Very Easy"){
                    diffParsed = "VeryEasy";
                }
                if (value.Difficulty_Category === "Very Hard"){
                    diffParsed = "VeryHard";
                }
                // Creating the individual class boxes
                if (value.Difficulty_Category === "Power Zone"){
                   data+= "<div class='myDiv box-shadow-hover pointer'><a href="+value.Workout_Link+"><h1><img src="+
                   value.Thumbnail+" height=222 width=333></h1><h2>"+value.Title+"</h2><h3>"+value.Release_Date+
                   "</h3><h3>"+value.Instructor+"</h3><h3> Difficulty: "+value.Peloton_Difficulty_Rating+
                   "</h3><h3> User Rating: "+value.User_Rating+"% </h3>";
                }
                else{
                   data+= "<div class='myDiv box-shadow-hover pointer'><a href="+value.Workout_Link+"><h1><img src="+
                   value.Thumbnail+" height=222 width=333></h1><h2>"+value.Title+"</h2><h3>"+value.Release_Date+
                   "</h3><h3>"+value.Instructor+ "    ·   <b class=" +diffParsed+ " >▊"+ value.Difficulty_Category +
                   "</b></h3><h3> Difficulty: "+value.Peloton_Difficulty_Rating+"</h3><h3> Output Range: "+
                   value.Expected_Min+" kJ - "+value.Expected_Max+" kJ</h3><h3> User Rating: "+value.User_Rating+"% </h3>";
                }
                data+="<h4>Artists: ";
                const songJSON = JSON.parse(value.Songs);
                for (let i=0; i<songJSON.length; i++){
                    if( i === 0 ){
                        data+=songJSON[i].Artist;
                    }
                    else{
                        data+=`, ${songJSON[i].Artist}`;
                    }
                }
                data+="</h4></div></a><br>";
            });
            $("#datalist").html(data);
            if (stopSearch === data){
                scrollEnabled = false;
            }

            /* Create Saved Search Link based on current search parameters */
            let shareableLink=`${window.location.protocol}//${window.location.host}/?`;
            if(titleLivebox){
                shareableLink+=`title=${encodeURIComponent(titleLivebox)}&`;
            }
            if(artistLivebox){
                shareableLink+=`artist=${encodeURIComponent(artistLivebox)}&`;
            }
            if(durationChosen && durationChosen.length){
                for (let j=0; j<durationChosen.length; j++){
                    shareableLink+=`duration=${encodeURIComponent(durationChosen[j])}&`;
                }
            }
            if(difficultyCatChosen && difficultyCatChosen.length){
                for (let j=0; j<difficultyCatChosen.length; j++){
                    shareableLink+=`difficulty=${encodeURIComponent(difficultyCatChosen[j])}&`;
                }
            }
            if(typeCatChosen && typeCatChosen.length){
                for (let j=0; j<typeCatChosen.length; j++){
                    shareableLink+=`category=${encodeURIComponent(typeCatChosen[j])}&`;
                }
            }
            if(excludeArtistBox === "exclude"){
                shareableLink+=`excludeartist${encodeURIComponent(excludeArtistBox)}&`;
            }
            if(instructorChosen && instructorChosen.length){
                for (let j=0; j<instructorChosen.length; j++){
                    shareableLink+=`instructor=${encodeURIComponent(instructorChosen[j])}&`;
                }
            }
            shareableLink+="autosubmit=1";
            $("#sharelink").html(shareableLink);
        }
    });
}



document.addEventListener('DOMContentLoaded',()=>{
    /* Chosen Initialization */
    $(".chosen-select").chosen();
    $(".chosen-select2").chosen();
    $(".chosen-select3").chosen();
    $(".chosen-select4").chosen();

    /* Pulling the search parameters from the URL. If autosubmit is enabled in the URL,
       it will also initiate the search on page load */
    let urlParams = new URLSearchParams(window.location.search);
    let titleParam= document.getElementById("title");
    let artistParam= document.getElementById("artist");
    let excludeArtistParam= document.getElementById("excludeartist");
    if (urlParams.get("title")){
        titleParam.value = urlParams.get("title");
    }
    if (urlParams.get("artist")){
        artistParam.value = urlParams.get("artist");
    }
    if (urlParams.get("excludeartist")){
        excludeArtistParam.checked = true;
    }
    $(".chosen-select4").val(urlParams.getAll('difficulty')).trigger("chosen:updated");
    $(".chosen-select3").val(urlParams.getAll('category')).trigger("chosen:updated");
    $(".chosen-select2").val(urlParams.getAll('duration')).trigger("chosen:updated");
    $(".chosen-select").val(urlParams.getAll('instructor')).trigger("chosen:updated");
    if(urlParams.get("autosubmit")!=="0") {
        setTimeout(function(){
            document.getElementById("submitBtn").click();
        }
        ,100);
    }

    /* Infinite scrolling implementation - Loads 10 new users when the bottom of the page is reached */
    window.addEventListener('scroll',() => {
        const scrollHeight = $(document).height();
        const scrollPos = Math.floor($(window).height() + $(window).scrollTop());
        const isBottom = scrollHeight - 800 < scrollPos;
        if (isBottom && (currentScrollHeight < scrollHeight) && scrollEnabled){
            searchIndex += 18;
            UpdateSearch();
            currentScrollHeight = scrollHeight;
        }
    });

   /* New Search query when user or other JS code clicks Submit  */
    document.getElementById("submitBtn").addEventListener('click', () => {
        data = "";
        searchIndex = 0;
        currentScrollHeight = 0;
        scrollEnabled = true;
        UpdateSearch();
   });
});