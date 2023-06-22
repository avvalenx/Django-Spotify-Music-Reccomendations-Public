function getArtists() {
    $.ajax({
        type: 'get',
        url: '/get_access_token',
        success: function(data) {
            const query = document.getElementById("search").value;
            const mydiv = document.getElementById('artists');
            const access = data['access'];
            $.ajax({
                url: 'https://api.spotify.com/v1/search',
                type: 'get',
                data: {
                    q: query,
                    type: 'artist',
                    limit: 10
                },
                headers: {'Authorization': 'Bearer ' + access},
                success: function (response) {
                    mydiv.innerHTML = "";
                    mydiv.classname = 'artists';
                    for (let a = 0; a < response['artists']['items'].length; a++) {
                        const artist = document.createElement("input");
                        artist.type = 'checkbox';
                        artist.value = response['artists']['items'][a]['id'];
                        artist.name = response['artists']['items'][a]['name'];
                        artist.class = 'checkbox';
                        artist.id = artist.value;

                        const artist_img = document.createElement("img");
                        artist_img.alt = 'artist image';
                        artist_img.src = response['artists']['items'][a]['images'][2]['url'];
                        artist_img.width = 100;
                        artist_img.height = 100;

                        const label = document.createElement("label");
                        label.innerHTML = response['artists']['items'][a]['name'];
                        label.htmlFor = artist.id;

                        const lineBreak = document.createElement("br");
                        mydiv.append(lineBreak);
                        mydiv.appendChild(artist);
                        mydiv.appendChild(label);
                        mydiv.appendChild(artist_img)
                    };
                },
                error: function (error) {
                    if (error['status'] == 401) {
                        $.ajax({
                            type: 'get',
                            url: '/expired_access_token',
                            success: function(data) {
                                getArtists();
                            }
                        });
                    } else {
                        $.ajax({
                            type: "POST",
                            url: "/error",
                            headers: {'X-CSRFToken': csrf_token},
                            data: {'error': 'unable to search for artists'},
                        });
                    }
                }
            });
        },
        error: function (error) {
            $.ajax({
                type: "POST",
                url: "/error",
                headers: {'X-CSRFToken': csrf_token},
                data: {'error': 'unable to get access token to search for artists'},
            });
        }
    });
}


const csrf_token = document.cookie.slice(10);

$("#submit-button").click(function(e) {
    e.preventDefault();
    var formData = {'artist013': 'placeholder'};
    $("input[name='artist']:checked").each(function() {
        formData[this.value] = this.value;
    });
    $.ajax({
        type: "POST",
        url: "/setup",
        headers: {'X-CSRFToken': csrf_token},
        data: formData,
        error: function() {
            $.ajax({
                type: "POST",
                url: "/error",
                headers: {'X-CSRFToken': csrf_token},
                data: {'error': 'unable to submit selected artists'},
            });
        }
    });
});