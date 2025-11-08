django.jQuery(document).ready(function($) {
    // Get the city, district, and neighborhood select elements
    var citySelect = $('#id_city');
    var districtSelect = $('#id_ilce');
    var neighborhoodSelect = $('#id_mahalle');

    // Function to update districts based on selected city
    function updateDistricts() {
        var cityName = citySelect.val();
        if (cityName) {
            $.ajax({
                url: '/admin/get-districts/',
                data: { city_name: cityName },
                success: function(data) {
                    districtSelect.empty();
                    districtSelect.append('<option value="">İlçe seçin...</option>');
                    $.each(data.districts, function(i, district) {
                        districtSelect.append('<option value="' + district.value + '">' + district.name + '</option>');
                    });
                    // Clear neighborhoods when city changes
                    neighborhoodSelect.empty();
                    neighborhoodSelect.append('<option value="">Mahalle seçin...</option>');
                }
            });
        } else {
            districtSelect.empty();
            districtSelect.append('<option value="">İlçe seçin...</option>');
            neighborhoodSelect.empty();
            neighborhoodSelect.append('<option value="">Mahalle seçin...</option>');
        }
    }

    // Function to update neighborhoods based on selected district
    function updateNeighborhoods() {
        var cityName = citySelect.val();
        var districtName = districtSelect.val();
        if (cityName && districtName) {
            $.ajax({
                url: '/admin/get-neighborhoods/',
                data: { 
                    city_name: cityName,
                    district_name: districtName 
                },
                success: function(data) {
                    neighborhoodSelect.empty();
                    neighborhoodSelect.append('<option value="">Mahalle seçin...</option>');
                    $.each(data.neighborhoods, function(i, neighborhood) {
                        neighborhoodSelect.append('<option value="' + neighborhood.value + '">' + neighborhood.name + '</option>');
                    });
                }
            });
        } else {
            neighborhoodSelect.empty();
            neighborhoodSelect.append('<option value="">Mahalle seçin...</option>');
        }
    }

    // Bind change events
    citySelect.change(updateDistricts);
    districtSelect.change(updateNeighborhoods);
});