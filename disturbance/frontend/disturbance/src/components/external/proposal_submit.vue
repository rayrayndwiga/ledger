<template lang="html">
    <div class="container" >
        <div class="row">
            <div class="col-sm-12">
                <div class="row">
                    <div v-if="proposal && proposal.id" class="col-sm-offset-3 col-sm-6 borderDecoration">
                        <strong>Your proposal has been successfully submitted.</strong>
                        <br/>
                        <table>
                            <tr>
                                <td><strong>Proposal:</strong></td>
                                <td><strong>{{proposal.id}}</strong></td>
                            </tr>
                            <tr>
                                <td><strong>Date/Time:</strong></td>
                                <td><strong> {{proposal.lodgement_date|formatDate}}</strong></td>
                            </tr>
                        </table>
                        <router-link :to="{name:'external-proposals-dash'}" style="margin-top:15px;" class="btn btn-primary">Back to dashboard</router-link>
                    </div>
                    <div v-else class="col-sm-offset-3 col-sm-6 borderDecoration">
                        <strong>Sorry it looks like there isn't any proposal currently in your session.</strong>
                        <br /><router-link :to="{name:'external-proposals-dash'}" style="margin-top:15px;" class="btn btn-primary">Back to dashboard</router-link>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import Vue from 'vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
import utils from './utils'
export default {
  data: function() {
    let vm = this;
    return {
        "proposal": {},
    }
  },
  components: {
  },
  computed: {
  },
  methods: {
  },
  filters:{
        formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY'): '';
        }
  },
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_proposal;
  },
  beforeRouteEnter: function(to, from, next) {
    next(vm => {
        vm.proposal = to.params.proposal;
    })
  }
}
</script>

<style lang="css" scoped>
.borderDecoration {
    border: 1px solid;
    border-radius: 5px;
    padding: 50px;
    margin-top: 70px;
}
</style>
