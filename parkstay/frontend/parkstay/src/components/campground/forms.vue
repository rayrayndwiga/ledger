<template lang="html">
   <div id='fields'>
      <div class="row">
          <div class="col-md-4" v-for="field in fields" >
            <div v-bind:class="{'form-group':true, 'has-error':field.error}">
              <label class="control-label" for="input">{{ field.name }}</label>
              <input :type="field.type" :name="filed.name" :value="field.val" :placeholder="field.placeholder" v-model="field.model" class="form-control">
            </div>
          </div>
       </div>

   </div>

</template>

<script>
module.exports = {
   name:'form',
   data:{
      return {

      }
   },
   props:{
      fields:{
         type:Object,
         required:true
      }
   }
}
</script>

<style lang="css">
</style>
