<template lang="html">
    <div class="container" >
        <form :action="proposal_form_url" method="post" name="new_proposal" enctype="multipart/form-data">
            <Proposal v-if="proposal" :proposal="proposal">
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                <input type='hidden' name="schema" :value="JSON.stringify(proposal)" />
                <input type='hidden' name="proposal_id" :value="1" />
                <div v-if="!proposal.readonly" class="row" style="margin-bottom:20px;">
                  <div class="col-lg-12 pull-right">
                        <input type="submit" class="btn btn-primary" value="Save and Exit"/>
                        <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                        <input type="button" @click.prevent="submit" class="btn btn-primary" value="Submit"/>
                  </div>
                </div>
                <div v-else class="row" style="margin-bottom:20px;">
                  <div class="col-lg-12 pull-right">
                    <router-link class="btn btn-primary" :to="{name: 'external-proposals-dash'}">Back to Dashboard</router-link>
                  </div>
                </div>
            </Proposal>
        </form>
    </div>
</template>
<script>
import Proposal from '../form.vue'
import Vue from 'vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  data: function() {
    return {
      "proposal": null,
      "loading": [],
      form: null,
    }
  },
  components: {
    Proposal
  },
  computed: {
    isLoading: function() {
      return this.loading.length > 0
    },
    csrf_token: function() {
      return helpers.getCookie('csrftoken')
    },
    proposal_form_url: function() {
      return (this.proposal) ? `/api/proposal/${this.proposal.id}/draft.json` : '';
    }
  },
  methods: {
    save: function(e) {
      let vm = this;
      let formData = new FormData(vm.form);
      vm.$http.post(vm.proposal_form_url,formData).then(res=>{
          swal(
            'Saved',
            'Your proposal has been saved',
            'success'
          )
      },err=>{

      });
    },
    submit: function(){
        let vm = this;
        
        swal({
            title: "Submit Proposal",
            text: "Are you sure you want to submit this proposal?",
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Submit'
        }).then(() => {
            let formData = new FormData(vm.form);
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/submit'),formData).then(res=>{
                vm.proposal = res.body;
                vm.$router.push({
                    name: 'submit_proposal',
                    params: { proposal: vm.proposal} 
                });
            },err=>{
                swal(
                    'Submit Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });
        },(error) => {
        });
    }
  },
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_proposal;
  },
  beforeRouteEnter: function(to, from, next) {
    if (to.params.proposal_id) {
      Vue.http.get(`/api/proposal/${to.params.proposal_id}.json`).then(res => {
          next(vm => {
            vm.loading.push('fetching proposal')
            vm.proposal = res.body;
            vm.loading.splice('fetching proposal', 1);
          });
        },
        err => {
          console.log(err);
        });
    }
    else {
      Vue.http.post('/api/proposal.json').then(res => {
          next(vm => {
            vm.loading.push('fetching proposal')
            vm.proposal = res.body;
            vm.loading.splice('fetching proposal', 1);
          });
        },
        err => {
          console.log(err);
        });
    }
  }
}
</script>

<style lang="css">
</style>
