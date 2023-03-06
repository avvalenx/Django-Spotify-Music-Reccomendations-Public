function getArtists() {
    $.ajax({
        type: 'get',
        url: '/get_access_token',
        success: function(data) {
            const query = document.getElementById("search").value;
            const mydiv = document.getElementById('artists');
            const access = data['access'];
            console.log(access);
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
                    for (let a = 0; a < response['artists']['items'].length; a++) {
                        const artist = document.createElement("input");
                        artist.type = 'checkbox';
                        artist.value = response['artists']['items'][a]['id'];
                        artist.name = response['artists']['items'][a]['name'];

                        const label = document.createElement("label");
                        label.innerHTML = response['artists']['items'][a]['name'];

                        mydiv.appendChild(artist);
                        mydiv.appendChild(label);
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
                    }
                }
            });
        },
        error: function (error) {
            console.log(error);
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
        success: function(data) {
            console.log(data);
        }
    });
});