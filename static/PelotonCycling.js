
function Copy() {
  let Url = document.getElementById("sharelink");
  Url.select();
  document.execCommand("copy");
}

$(".chosen-select").chosen({no_results_text: "Oops, nothing found!"});
$(".chosen-select2").chosen({no_results_text: "Oops, nothing found!"});
$(".chosen-select3").chosen({no_results_text: "Oops, nothing found!"});
$(".chosen-select4").chosen({no_results_text: "Oops, nothing found!"});
//$(".chosen-results").css('font-size','20px');


let queryString = window.location.search;
let urlParams = new URLSearchParams(queryString);
let currentLocation = window.location.protocol+"//"+window.location.host;
let searched = false;
let searchIndex = 0;
let data = "";
let scrollReady = true;


function UpdateSearch(){
    let titleLivebox = $("#title").val();
    let artistLivebox = $("#artist").val();
    let difficultyCatChosen = $("#multdifficultycat").val();
    let typeCatChosen = $("#multtypecat").chosen().val();
    let durationChosen = $("#multDuration").chosen().val();
    let instructorChosen = $("#instructorlist").chosen().val();
    let excludeArtistbox = "";
    if ($("#excludeartist").is(":checked")){
        excludeArtistbox = "exclude";
    }
    else{
        excludeArtistbox = "include";
    }

    /* Current hacky solution for artists search since the artist filtering is happening outside of the SQL query.
    Doesn't allow dynamic loading if you do a song artist search since it already requests all the records with no limit.
    Need to figure out a way to search the song JSON in the SQL query so I don't have to do this junk*/
    if (artistLivebox){
        scrollReady = false;
    }
    else{
        scrollReady = true;
    }
    searched = true;


    $.ajax({
        method:"POST",
        url:"/PelotonSearch",
        data:{title:titleLivebox, difficulty_cat_chosen:difficultyCatChosen, duration_chosen:durationChosen, instructor_chosen:instructorChosen, type_cat_chosen:typeCatChosen, artist:artistLivebox, exclude_artist:excludeArtistbox, search_index:searchIndex},
        success:function(res){
            //console.log(res);
            let stopSearch = data;
            $.each(res,function(index,value){
                let diffParsed = value.Difficulty_Category;
                if (value.Difficulty_Category === "Very Easy"){
                    diffParsed = "VeryEasy"
                }
                if (value.Difficulty_Category === "Very Hard"){
                    diffParsed = "VeryHard"
                }
                if (value.Difficulty_Category === "Power Zone")
                {
                   data+= "<div class=myDiv style='margin: auto;'><a href="+value.Workout_Link+"><h1><img src="+value.Thumbnail+" height=240 width=360></h1><h2>"+value.Title+"</h2><h3>"+value.Release_Date+
                   "</h3><h3>"+value.Instructor+"</h3><h3> Difficulty: "+value.Peloton_Difficulty_Rating+"</h3><h3> User Rating: "+value.User_Rating+"% </h3>";
                }
                else
                {
                   data+= "<div class=myDiv style='margin: auto;'><a href="+value.Workout_Link+"><h1><img src="+value.Thumbnail+" height=240 width=360></h1><h2>"+value.Title+"</h2><h3>"+value.Release_Date+
                   "</h3><h3>"+value.Instructor+ "    ·   <b class=" +diffParsed+ " >▊"+ value.Difficulty_Category +"</b></h3><h3> Difficulty: "+value.Peloton_Difficulty_Rating+
                   "</h3><h3> Output Range: "+value.Expected_Min+" kJ - "+value.Expected_Max+" kJ</h3><h3> User Rating: "+value.User_Rating+"% </h3>";
                }
                data+="<h4>Artists: ";
                let songJSON = JSON.parse(value.Songs);
                for (let i=0; i<songJSON.length; i++){
                    if( i === 0 ){
                        data+=songJSON[i].Artist;
                    }
                    else{
                        data+=", "+ songJSON[i].Artist;
                    }
                }
                data+="</h4></div></a><br>";
            });
            $("#datalist").html(data);
            if (stopSearch === data){
                searched = false;
            }

            /* Create Saved Search Link based on current search parameters*/
            let shareableLink=currentLocation+"/?";
            if(titleLivebox){
                shareableLink+="title="+encodeURIComponent(titleLivebox)+"&";
            }
            if(artistLivebox){
                shareableLink+="artist="+encodeURIComponent(artistLivebox)+"&";
            }
            if(durationChosen){
                for (let j=0; j<durationChosen.length; j++){
                    shareableLink+="duration="+encodeURIComponent(durationChosen[j])+"&";
                }
            }
            if(difficultyCatChosen){
                for (let j=0; j<difficultyCatChosen.length; j++){
                    shareableLink+="difficulty="+encodeURIComponent(difficultyCatChosen[j])+"&";
                }
            }
            if(typeCatChosen){
                for (let j=0; j<typeCatChosen.length; j++){
                    shareableLink+="category="+encodeURIComponent(typeCatChosen[j])+"&";
                }
            }
            if(excludeArtistbox === "exclude"){
                shareableLink+="excludeartist="+encodeURIComponent(excludeArtistbox)+"&";
            }
            if(instructorChosen){
                for (let j=0; j<instructorChosen.length; j++){
                    shareableLink+="instructor="+encodeURIComponent(instructorChosen[j])+"&";
                }
            }
            shareableLink+="autosubmit=1"
            $("#sharelink").html(shareableLink);
        }
    })
}

$(document).ready(function(e){
    /* Pulling the search parameters from the URL. If autosubmit is enabled in the URL,
       it will also initiate the search on page load */
    let titleParam= document.getElementById("title");
    let artistParam= document.getElementById("artist");
    let excludeartistParam= document.getElementById("excludeartist")
    if (urlParams.get("title")){
        titleParam.value = urlParams.get("title");
        }
    if (urlParams.get("artist")){
        artistParam.value = urlParams.get("artist");
        }
    if (urlParams.get("excludeartist")){
        excludeartistParam.checked = true;
        }
    $(".chosen-select4").val(urlParams.getAll('difficulty')).trigger("chosen:updated");
    $(".chosen-select3").val(urlParams.getAll('category')).trigger("chosen:updated");
    $(".chosen-select2").val(urlParams.getAll('duration')).trigger("chosen:updated");
    $(".chosen-select").val(urlParams.getAll('instructor')).trigger("chosen:updated");
    if(urlParams.get("autosubmit")!=="0") {
        setTimeout(function(){$("#submitBtn").click()},100);
    }

    /* Loads 10 new records if the user scrolls to the end of page.*/
    $(window).scroll(function() {
        var nearToBottom = 110;
        if (($(window).scrollTop() + $(window).height() > $(document).height() - nearToBottom) && searched && scrollReady) {
            scrollReady = false;
            searchIndex += 10;
            setTimeout(function(){
                UpdateSearch();
                scrollReady= true;
            },100);
        }
    });

   /* New search done when user or JS clicks Submit button*/
   $("#submitBtn").on("click",function(e){
        data = "";
        searchIndex = 0;
        UpdateSearch();
   });
})