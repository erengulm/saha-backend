// Global functions that can be called from inline event handlers
function updateDistricts() {
    console.log('=== updateDistricts() called ===');
    var citySelect = django.jQuery('#id_city');
    var districtSelect = django.jQuery('#id_ilce');
    var neighborhoodSelect = django.jQuery('#id_mahalle');
    
    var cityName = citySelect.val();
    console.log('Selected city:', cityName);
    
    if (!cityName || cityName.trim() === '') {
        console.log('No city selected, clearing dropdowns');
        districtSelect.empty().append('<option value="">İlçe seçin</option>').prop('disabled', true);
        neighborhoodSelect.empty().append('<option value="">Mahalle seçin</option>').prop('disabled', true);
        return;
    }
    
    console.log('Fetching districts for:', cityName);
    districtSelect.empty().append('<option value="">Yükleniyor...</option>').prop('disabled', true);
    neighborhoodSelect.empty().append('<option value="">Mahalle seçin</option>').prop('disabled', true);
    
    django.jQuery.ajax({
        url: '/admin/get-districts/',
        type: 'GET',
        data: { city_name: cityName },
        success: function(data) {
            console.log('Districts received:', data);
            districtSelect.empty().append('<option value="">İlçe seçin</option>');
            
            if (data && data.districts && data.districts.length > 0) {
                django.jQuery.each(data.districts, function(i, district) {
                    districtSelect.append('<option value="' + district.value + '">' + district.name + '</option>');
                });
                districtSelect.prop('disabled', false);
                console.log('Districts populated successfully');
            } else {
                districtSelect.append('<option value="">İlçe bulunamadı</option>').prop('disabled', true);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error fetching districts:', error);
            districtSelect.empty().append('<option value="">Hata oluştu</option>').prop('disabled', true);
        }
    });
}

function updateNeighborhoods() {
    console.log('=== updateNeighborhoods() called ===');
    var citySelect = django.jQuery('#id_city');
    var districtSelect = django.jQuery('#id_ilce');
    var neighborhoodSelect = django.jQuery('#id_mahalle');
    
    var cityName = citySelect.val();
    var districtName = districtSelect.val();
    console.log('Selected city:', cityName, 'district:', districtName);
    
    if (!cityName || !districtName) {
        console.log('Missing city or district');
        neighborhoodSelect.empty().append('<option value="">Mahalle seçin</option>').prop('disabled', true);
        return;
    }
    
    console.log('Fetching neighborhoods...');
    neighborhoodSelect.empty().append('<option value="">Yükleniyor...</option>').prop('disabled', true);
    
    django.jQuery.ajax({
        url: '/admin/get-neighborhoods/',
        type: 'GET',
        data: { 
            city_name: cityName,
            district_name: districtName 
        },
        success: function(data) {
            console.log('Neighborhoods received:', data);
            neighborhoodSelect.empty().append('<option value="">Mahalle seçin</option>');
            
            if (data && data.neighborhoods && data.neighborhoods.length > 0) {
                django.jQuery.each(data.neighborhoods, function(i, neighborhood) {
                    neighborhoodSelect.append('<option value="' + neighborhood.value + '">' + neighborhood.name + '</option>');
                });
                neighborhoodSelect.prop('disabled', false);
                console.log('Neighborhoods populated successfully');
            } else {
                neighborhoodSelect.prop('disabled', true);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error fetching neighborhoods:', error);
            neighborhoodSelect.empty().append('<option value="">Hata oluştu</option>').prop('disabled', true);
        }
    });
}

// Initialize existing values on page load
function initializeExistingValues() {
    console.log('=== initializeExistingValues() called ===');
    var citySelect = django.jQuery('#id_city');
    var districtSelect = django.jQuery('#id_ilce');
    var neighborhoodSelect = django.jQuery('#id_mahalle');
    
    // Get the values that Django has set in the form (from the database)
    var savedCity = citySelect.val();
    var savedDistrict = districtSelect.find('option:selected').val() || districtSelect.val();
    var savedNeighborhood = neighborhoodSelect.find('option:selected').val() || neighborhoodSelect.val();
    
    console.log('Form loaded values - City:', savedCity, 'District:', savedDistrict, 'Neighborhood:', savedNeighborhood);
    
    // Also check if there are any selected options in the original form
    var originalDistrict = districtSelect.find('option:selected').text();
    var originalNeighborhood = neighborhoodSelect.find('option:selected').text();
    console.log('Original selected text - District:', originalDistrict, 'Neighborhood:', originalNeighborhood);
    
    if (savedCity && savedCity.trim() !== '') {
        console.log('Found saved city, loading districts...');
        
        // Load districts for the saved city
        django.jQuery.ajax({
            url: '/admin/get-districts/',
            type: 'GET',
            data: { city_name: savedCity },
            success: function(data) {
                console.log('Districts loaded for initialization:', data);
                districtSelect.empty().append('<option value="">İlçe seçin</option>');
                
                if (data && data.districts && data.districts.length > 0) {
                    django.jQuery.each(data.districts, function(i, district) {
                        var option = django.jQuery('<option></option>')
                            .attr('value', district.value)
                            .text(district.name);
                        
                        // Select the saved district if it matches (check both value and name)
                        if ((savedDistrict && district.value === savedDistrict) || 
                            (originalDistrict && district.name === originalDistrict)) {
                            option.attr('selected', 'selected');
                            console.log('Restored district selection:', district.name);
                            savedDistrict = district.value; // Update savedDistrict for neighborhood loading
                        }
                        
                        districtSelect.append(option);
                    });
                    districtSelect.prop('disabled', false);
                    
                    // If we have a saved district, load neighborhoods
                    if (savedDistrict && savedDistrict.trim() !== '') {
                        console.log('Found saved district, loading neighborhoods...');
                        
                        django.jQuery.ajax({
                            url: '/admin/get-neighborhoods/',
                            type: 'GET',
                            data: { 
                                city_name: savedCity,
                                district_name: savedDistrict 
                            },
                            success: function(data) {
                                console.log('Neighborhoods loaded for initialization:', data);
                                neighborhoodSelect.empty().append('<option value="">Mahalle seçin</option>');
                                
                                if (data && data.neighborhoods && data.neighborhoods.length > 0) {
                                    django.jQuery.each(data.neighborhoods, function(i, neighborhood) {
                                        var option = django.jQuery('<option></option>')
                                            .attr('value', neighborhood.value)
                                            .text(neighborhood.name);
                                        
                                        // Select the saved neighborhood if it matches (check both value and name)
                                        if ((savedNeighborhood && neighborhood.value === savedNeighborhood) ||
                                            (originalNeighborhood && neighborhood.name === originalNeighborhood)) {
                                            option.attr('selected', 'selected');
                                            console.log('Restored neighborhood selection:', neighborhood.name);
                                        }
                                        
                                        neighborhoodSelect.append(option);
                                    });
                                    neighborhoodSelect.prop('disabled', false);
                                } else {
                                    neighborhoodSelect.prop('disabled', true);
                                }
                            },
                            error: function(xhr, status, error) {
                                console.error('Error loading neighborhoods for initialization:', error);
                                neighborhoodSelect.prop('disabled', true);
                            }
                        });
                    } else {
                        neighborhoodSelect.prop('disabled', true);
                    }
                } else {
                    districtSelect.prop('disabled', true);
                    neighborhoodSelect.prop('disabled', true);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error loading districts for initialization:', error);
                districtSelect.prop('disabled', true);
                neighborhoodSelect.prop('disabled', true);
            }
        });
    } else {
        // No saved city, disable dependent dropdowns
        districtSelect.prop('disabled', true);
        neighborhoodSelect.prop('disabled', true);
    }
}

// Initialize on page load
django.jQuery(document).ready(function($) {
    console.log('User admin JS loaded - using inline event handlers');
    
    // Initial setup
    var districtSelect = $('#id_ilce');
    var neighborhoodSelect = $('#id_mahalle');
    var citySelect = $('#id_city');
    
    // Wait a bit for Django to fully load the form values, then initialize
    setTimeout(function() {
        console.log('Delayed initialization starting...');
        initializeExistingValues();
    }, 500); // 500ms delay to ensure form is fully loaded
    
    console.log('Initial setup complete');
});