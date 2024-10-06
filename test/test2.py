w = 0

                    for i in self.vector:
                        tmp_field_set.append(self.field_bias)
                        tmp_field_angle.append(self.field_angle)

                        self.keithley.source_voltage = i
                        sleep(self.delay * 0.001)
                        if self.agilent == True:
                            self.tmp_current = self.agilent_34410.current_dc
                        else:
                            self.tmp_current = self.keithley.current
                        sleep(self.delay * 0.001)
                        
                        if self.field_device == "2D Controller":
                            self.tmp_field = self.field.get_field()
                            tmp_field_x.append(self.tmp_field[0])
                            tmp_field_y.append(self.tmp_field[1])
                            tmp_field_z.append(self.tmp_field[2])


                        else:
                            self.tmp_field = self.field_sensor.read_field()
                            tmp_field_x.append(self.tmp_field[0])
                            tmp_field_y.append(self.tmp_field[1])
                            tmp_field_z.append(self.tmp_field[2])
                        
                        
                        
                        # surowe
                        tmp_current.append(self.tmp_current)
                        tmp_voltage.append(i)
                        tmp_resistance.append(
                            float(i) / float(self.tmp_current)
                            if self.tmp_current != 0
                            else math.nan
                        )
                        tmp_conductance.append(
                            1 / (float(i) / float(self.tmp_current))
                            if self.tmp_current != 0 and i != 0
                            else math.nan
                        )

                        self.emit("progress", 100 * w / len(self.vector))
                        w = w + 1
                        if self.should_stop():
                            log.warning("USER STOP")
                            break

                    # opracowanie:
                    tmp_dI_dV = diff.diffs(tmp_voltage, tmp_current)
                    tmp_dI = diff.diffIV(tmp_current)
                    tmp_dR = diff.diffIV(tmp_resistance)
                    tmp_dG = diff.diffIV(tmp_conductance)

                    for l in range(len(tmp_voltage)):
                        data = {
                            "V (V)": self.value_function(tmp_voltage, l),
                            "I (A)": self.value_function(tmp_current, l),
                            "R (ohm)": self.value_function(tmp_resistance, l),
                            "G": self.value_function(tmp_conductance, l),
                            "X field (Oe)": self.value_function(tmp_field_x, l),
                            "Y field (Oe)": self.value_function(tmp_field_y, l),
                            "Z field (Oe)": self.value_function(tmp_field_z, l),
                            "Hset (Oe)": self.value_function(tmp_field_set, l),
                            "dI": self.value_function(tmp_dI, l),
                            "dI/dV": self.value_function(tmp_dI_dV, l),
                            "dR": self.value_function(tmp_dR, l),
                            "dG": self.value_function(tmp_dG, l),
                            "Phase": self.value_function(tmp_field_angle, l)
                        }
                        self.emit("results", data)
                        stop_flag = False