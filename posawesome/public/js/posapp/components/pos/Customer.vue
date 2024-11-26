<style scoped>
.bordered-input .v-input__control {
  border: 1px solid #0097A7;
}

.bordered-input .v-input__control:focus-within {
  border-color: #0097A7;
}

.bordered-input .v-input__slot {
  border: none;
  /* Remove default border */
}
</style>

<template>
  <div>
    <v-autocomplete dense clearable auto-select-first outlined color="primary" :label="frappe._('Select Customer')"
      v-model="customer" :items="filteredCustomers" item-text="customer_name" item-value="name" background-color="white"
      :no-data-text="__('Customer not found')" hide-details :disabled="readonly" append-icon="mdi-plus"
      @click:append="new_customer" prepend-inner-icon="mdi-account-edit"
      @click:prepend-inner="edit_customer">
      <template v-slot:prepend>
        <v-text-field v-model="searchQuery" label="Search Customer Name / Mobile" @keyup.enter="searchCustomers" append-icon="mdi-magnify"
          @click:append="searchCustomers" dense hide-details outlined :style="{ borderColor: '#0097A7', width: '300px', marginTop: '-7px' }"
          class="bordered-input search-field"></v-text-field>
      </template>
      <template v-slot:item="data">
        <v-list-item-content>
          <v-list-item-title class="primary--text subtitle-1" v-html="data.item.customer_name"></v-list-item-title>
          <v-list-item-subtitle v-if="data.item.customer_name != data.item.name"
            v-html="`ID: ${data.item.name}`"></v-list-item-subtitle>
          <v-list-item-subtitle v-if="data.item.mobile_no"
            v-html="`Mobile No: ${data.item.mobile_no}`"></v-list-item-subtitle>
        </v-list-item-content>
      </template>
    </v-autocomplete>
  </div>
</template>
<script>
import { evntBus } from '../../bus';
export default {
  data: () => ({
    pos_profile: '',
    customers: [],
    filteredCustomers: [],
    customer: '',
    searchQuery: '',
    readonly: false,
  }),

  methods: {
    get_customer_names() {
      const vm = this;
      if (vm.pos_profile.posa_local_storage && localStorage.customer_storage) {
        vm.customers = JSON.parse(localStorage.getItem('customer_storage'));
      }
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.get_customer_names',
        args: {
          pos_profile: this.pos_profile.pos_profile,
        },
        callback: function (r) {
          if (r.message) {
            vm.customers = r.message;
            console.log(r.message);
            vm.filteredCustomers = r.message; // Initialize filteredCustomers
            console.info('loadCustomers');
            if (vm.pos_profile.posa_local_storage) {
              localStorage.setItem('customer_storage', '');
              localStorage.setItem(
                'customer_storage',
                JSON.stringify(r.message)
              );
            }
          }
        },
      });
    },
    searchCustomers() {
      this.filteredCustomers = this.customers.filter(customer => {
        const searchText = this.searchQuery.toLowerCase();
        return (
          customer.customer_name.toLowerCase().includes(searchText) ||
          customer.name.toLowerCase().includes(searchText) ||
          (customer.mobile_no && customer.mobile_no.toString().toLowerCase().includes(searchText)) // Convert to string
        );
      });
    }
    ,
    new_customer() {
      evntBus.$emit('open_new_customer');
    },
    edit_customer() {
      evntBus.$emit('open_edit_customer');
    },
  },

  created: function () {
    this.$nextTick(function () {
      evntBus.$on('register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        this.get_customer_names();
      });
      evntBus.$on('set_customer', (customer) => {
        this.customer = customer;
      });
      evntBus.$on('add_customer_to_list', (customer) => {
        this.customers.push(customer);
      });
      evntBus.$on('set_customer_readonly', (value) => {
        this.readonly = value;
      });
    });
  },

  watch: {
    customer() {
      evntBus.$emit('update_customer', this.customer);
    },
  },
};
</script>
