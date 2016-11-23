/* global angular */
(function () {
    'use strict';

    angular
        .module('plugins.pending')
        .component('pendingView', {
            templateUrl: 'plugins/pending/pending.tmpl.html',
            controllerAs: 'vm',
            controller: pendingController
        });

    function pendingController($filter, pendingService) {
        var vm = this;

        vm.$onInit = activate;
        vm.approveEntry = approveEntry;
        vm.deleteEntry = deleteEntry;
            
        function activate() {
            getPending();
        }

        function getPending() {
            pendingService.getPending()
                .then(setEntries)
                .cached(setEntries);
        }

        function approveEntry(id) {
            pendingService.approveEntry(id)
                .then(function (response) {
                    var filtered = $filter('filter')(vm.entries, { id: id });
                    var index = vm.entries.indexOf(filtered[0]);
                    vm.entries[index] = response.data;
                });
        }

        function deleteEntry(id) {
            pendingService.deleteEntry(id)
                .then(function (response) {
                    var filtered = $filter('filter')(vm.entries, { id: id });
                    var index = vm.entries.indexOf(filtered[0]);
                    vm.entries.splice(index, 1);
                });
        }
        
        function setEntries(response) {
            vm.entries = response.data;
        }
    }
}());